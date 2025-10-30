"""
LangGraph Planner Routes
LangGraph-based autonomous planner for advanced workflow creation

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify
import uuid
import json
from datetime import datetime


class LGraphPlannerRoutes:
    """LangGraph planner routes handler"""
    
    def __init__(self, app, user_registry, get_db, login_required):
        self.app = app
        self.user_registry = user_registry
        self.get_db = get_db
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all LangGraph planner routes"""
        
        @self.app.route('/lgraph/planner')
        @self.login_required
        def lgraph_planner_page():
            """LangGraph autonomous planner interface"""
            from workflows.lgraph.lgraph_planner import LangGraphPlanner as LGraphPlanner
            
            user = self.user_registry.get_user(session['user_id'])
            user_id = session.get('user_id', 'demo_user')
            session_id = str(uuid.uuid4())

            try:
                planner = LGraphPlanner()

                # Get user's pending and approved plans
                pending_plans = planner.get_user_plans(user_id, status='pending_approval')
                approved_plans = planner.get_user_plans(user_id, status='approved')
            except Exception as e:
                pending_plans = []
                approved_plans = []

            return render_template(
                'lgraph_planner.html',
                user=user,
                session_id=session_id,
                pending_plans=pending_plans,
                approved_plans=approved_plans
            )
        
        @self.app.route('/api/lgraph/planner/chat', methods=['POST'])
        def api_lgraph_planner_chat():
            """Chat with the LangGraph planner"""
            from workflows.lgraph.lgraph_planner import LangGraphPlanner as LGraphPlanner
            
            try:
                data = request.get_json()
                message = data.get('message', '')
                history = data.get('history', [])
                session_id = data.get('session_id', str(uuid.uuid4()))

                if not message:
                    return jsonify({'error': 'Message is required'}), 400

                user_id = session.get('user_id', 'demo_user')

                planner = LGraphPlanner()
                result = planner.chat(
                    user_id=user_id,
                    message=message,
                    conversation_history=history
                )

                return jsonify({
                    'response': result['response'],
                    'conversation_id': result.get('conversation_id'),
                    'timestamp': result.get('timestamp')
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/lgraph/create-plan')
        @self.login_required
        def create_autonomous_plan_page():
            """Display the create autonomous plan form"""
            user = self.user_registry.get_user(session['user_id'])
            return render_template('create_autonomous_plan.html', user=user)
        
        @self.app.route('/api/lgraph/create-plan', methods=['POST'])
        def api_lgraph_create_plan():
            """Create a new autonomous plan using LangGraph"""
            from workflows.lgraph.lgraph_planner import LangGraphPlanner as LGraphPlanner
            
            try:
                data = request.get_json()
                user_request = data.get('user_request', '')
                options = data.get('options', {})
                session_id = data.get('session_id', str(uuid.uuid4()))

                if not user_request:
                    return jsonify({
                        'success': False,
                        'error': 'User request is required'
                    }), 400

                user_id = session.get('user_id', 'demo_user')

                planner = LGraphPlanner()
                result = planner.create_autonomous_plan(
                    user_id=user_id,
                    user_request=user_request,
                    session_id=session_id,
                    options=options
                )

                return jsonify({
                    'success': True,
                    'plan_id': result['plan_id'],
                    'plan_type': result.get('plan_type', 'StateGraph'),
                    'node_count': result.get('node_count', 0),
                    'message': result.get('message', 'Plan created successfully')
                })

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/lgraph/plan/<plan_id>')
        @self.login_required
        def lgraph_plan_detail(plan_id):
            """Display details of a specific LangGraph plan"""
            from workflows.lgraph.lgraph_planner import LangGraphPlanner as LGraphPlanner
            
            user = self.user_registry.get_user(session['user_id'])
            user_id = session.get('user_id', 'demo_user')

            try:
                planner = LGraphPlanner()
                plan = planner.get_plan(plan_id)

                if not plan:
                    flash('Plan not found', 'danger')
                    return redirect(url_for('lgraph_planner_page'))

                # Verify user owns this plan
                if plan.get('user_id') != user_id:
                    flash('Unauthorized access to plan', 'danger')
                    return redirect(url_for('lgraph_planner_page'))
            except Exception as e:
                flash(f'Error loading plan: {str(e)}', 'danger')
                return redirect(url_for('lgraph_planner_page'))

            return render_template('lgraph_plan_detail.html', user=user, plan=plan)
        
        @self.app.route('/api/lgraph/plan/<plan_id>/approve', methods=['POST'])
        def api_lgraph_approve_plan(plan_id):
            """Approve a LangGraph autonomous plan"""
            from workflows.lgraph.lgraph_planner import LangGraphPlanner as LGraphPlanner
            
            try:
                planner = LGraphPlanner()
                planner.approve_plan(plan_id)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/lgraph/plan/<plan_id>/reject', methods=['POST'])
        def api_lgraph_reject_plan(plan_id):
            """Reject a LangGraph autonomous plan"""
            from workflows.lgraph.lgraph_planner import LangGraphPlanner as LGraphPlanner
            
            try:
                data = request.get_json() or {}
                reason = data.get('reason', '')

                planner = LGraphPlanner()
                planner.reject_plan(plan_id, reason)
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/lgraph/plan/<plan_id>/execute', methods=['POST'])
        def api_lgraph_execute_plan(plan_id):
            """Execute a LangGraph autonomous plan"""
            from workflows.lgraph.lgraph_planner import LangGraphPlanner as LGraphPlanner
            
            try:
                user_id = session.get('user_id', 'demo_user')

                planner = LGraphPlanner()
                plan = planner.get_plan(plan_id)

                if not plan:
                    return jsonify({'success': False, 'error': 'Plan not found'}), 404

                if plan.get('status') != 'approved':
                    return jsonify({'success': False, 'error': 'Plan must be approved before execution'}), 400

                # Create execution record
                execution_id = str(uuid.uuid4())
                db = self.get_db()

                db.insert('workflow_executions', {
                    'execution_id': execution_id,
                    'dag_id': plan_id,
                    'user_id': user_id,
                    'status': 'running',
                    'start_time': datetime.now().isoformat()
                })

                # In a real implementation, this would:
                # 1. Initialize the StateGraph
                # 2. Execute nodes in order
                # 3. Handle parallel execution
                # 4. Pause at HITL checkpoints
                # 5. Collect results

                # For now, simulate completion
                db.update(
                    'workflow_executions',
                    {
                        'status': 'completed',
                        'end_time': datetime.now().isoformat(),
                        'results': json.dumps({
                            'message': 'Autonomous execution completed',
                            'plan_type': plan.get('plan_type', 'StateGraph')
                        })
                    },
                    'execution_id = ?',
                    (execution_id,)
                )

                return jsonify({'success': True, 'execution_id': execution_id})

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
