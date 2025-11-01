"""
Planner Routes
DAG-based planner for creating and managing execution plans

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify
import uuid
import json
from datetime import datetime
from routes.base_routes import BaseRoutes

class PlannerRoutes(BaseRoutes):
    """Planner routes handler"""
    
    def __init__(self, app, user_registry, planner, tool_registry, agent_registry, dag_registry, orchestrator, get_db, login_required):
        super().__init__()

        self.app = app
        self.user_registry = user_registry
        self.planner = planner
        self.tool_registry = tool_registry
        self.agent_registry = agent_registry
        self.dag_registry = dag_registry
        self.orchestrator = orchestrator
        self.get_db = get_db
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all planner routes"""
        
        @self.app.route('/planner')
        @self.login_required
        def planner_page():
            """Planner chat interface"""
            user = self.user_registry.get_user(session['user_id'])

            # Get recent conversations
            conversations = self.planner.get_conversation_history(user.user_id, limit=20)

            # Get user's pending plans
            plans = self.planner.get_user_plans(user.user_id)
            pending_plans = [p for p in plans if p['status'] == 'pending_approval']

            return render_template('planner.html',
                                 user=user,
                                 conversations=conversations,
                                 pending_plans=pending_plans)
        
        @self.app.route('/create_plan')
        @self.login_required
        def create_plan_page():
            """Create plan page"""
            user = self.user_registry.get_user(session['user_id'])
            return render_template('create_plan.html', user=user)
        
        @self.app.route('/api/planner/chat', methods=['POST'])
        @self.login_required
        def api_planner_chat():
            """API endpoint for planner chat"""
            data = request.get_json()
            message = data.get('message', '')
            conversation_history = data.get('history', [])

            response = self.planner.chat(session['user_id'], message, conversation_history)

            return jsonify({
                'success': True,
                'response': response['response'],
                'timestamp': response['timestamp']
            })
        
        @self.app.route('/api/planner/create_plan', methods=['POST'])
        @self.login_required
        def api_planner_create_plan():
            """API endpoint to create a plan from request"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()
            request_text = data.get('request', '')

            # Get available tools and agents for this user
            all_tools = self.tool_registry.list_tools()
            all_agents = self.agent_registry.list_agents()

            available_tools = [t['tool_name'] for t in all_tools if user.has_tool_access(t['tool_name'])]
            available_agents = [a['agent_id'] for a in all_agents if user.has_agent_access(a['agent_id'])]

            result = self.planner.create_plan_from_request(
                user.user_id,
                request_text,
                available_tools,
                available_agents
            )

            return jsonify({
                'success': True,
                'plan_id': result['plan_id'],
                'plan': result['plan'],
                'message': result['message']
            })
        
        @self.app.route('/plan/<plan_id>')
        @self.login_required
        def plan_detail(plan_id):
            """Plan review page"""
            user = self.user_registry.get_user(session['user_id'])

            plan_data = self.planner.get_plan(plan_id)
            if not plan_data:
                flash('Plan not found', 'danger')
                return redirect(url_for('planner_page'))

            # Check if user owns this plan or is admin
            if plan_data['user_id'] != user.user_id and not user.is_admin():
                flash('Access denied', 'danger')
                return redirect(url_for('planner_page'))

            return render_template('plan_detail.html', user=user, plan=plan_data)
        
        @self.app.route('/api/plan/approve/<plan_id>', methods=['POST'])
        @self.login_required
        def api_approve_plan(plan_id):
            """Approve a plan"""
            user = self.user_registry.get_user(session['user_id'])

            plan_data = self.planner.get_plan(plan_id)
            if not plan_data or (plan_data['user_id'] != user.user_id and not user.is_admin()):
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            self.planner.approve_plan(plan_id)

            return jsonify({'success': True, 'message': 'Plan approved'})
        
        @self.app.route('/api/plan/reject/<plan_id>', methods=['POST'])
        @self.login_required
        def api_reject_plan(plan_id):
            """Reject a plan"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()
            reason = data.get('reason', '')

            plan_data = self.planner.get_plan(plan_id)
            if not plan_data or (plan_data['user_id'] != user.user_id and not user.is_admin()):
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            self.planner.reject_plan(plan_id, reason)

            return jsonify({'success': True, 'message': 'Plan rejected'})
        
        @self.app.route('/api/plan/execute/<plan_id>', methods=['POST'])
        @self.login_required
        def api_execute_plan(plan_id):
            """Execute an approved plan"""
            user = self.user_registry.get_user(session['user_id'])

            plan_data = self.planner.get_plan(plan_id)
            if not plan_data:
                return jsonify({'success': False, 'error': 'Plan not found'}), 404

            if plan_data['status'] != 'approved':
                return jsonify({'success': False, 'error': 'Plan must be approved first'}), 400

            # Create graph from plan
            plan = plan_data['plan']
            graph = self.dag_registry.create_graph_from_dag(plan['dag_id'])

            if not graph:
                # Create graph from plan definition
                from graph.graph import Graph, Node, Edge
                graph = Graph(
                    graph_id=plan['dag_id'],
                    name=plan['name'],
                    description=plan['description']
                )

                for node_config in plan['nodes']:
                    node = Node(
                        node_id=node_config['node_id'],
                        node_type=node_config['node_type'],
                        agent_id=node_config.get('agent_id'),
                        config=node_config.get('config', {})
                    )
                    graph.add_node(node)

                for node_config in plan['nodes']:
                    node_id = node_config['node_id']
                    for dep in node_config.get('dependencies', []):
                        edge = Edge(from_node=dep, to_node=node_id)
                        graph.add_edge(edge)

                graph.start_nodes = plan.get('start_nodes', [])

            # Create session
            session_id = str(uuid.uuid4())
            db = self.get_db()
            db.insert('sessions', {
                'session_id': session_id,
                'user_id': user.user_id,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'metadata': json.dumps({'plan_id': plan_id})
            })

            # Start workflow
            workflow_id = self.orchestrator.start_workflow(plan['dag_id'], session_id, user.user_id, graph)

            # Update plan status
            db.update('plans', {'status': 'executed'}, 'plan_id = ?', (plan_id,))

            return jsonify({
                'success': True,
                'workflow_id': workflow_id,
                'message': 'Plan execution started'
            })
