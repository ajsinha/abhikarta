"""
Agent Routes
Agent management, execution, and administration

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify


class AgentRoutes:
    """Agent routes handler"""
    
    def __init__(self, app, user_registry, agent_registry, login_required):
        self.app = app
        self.user_registry = user_registry
        self.agent_registry = agent_registry
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all agent routes"""
        
        # ============== AGENT LISTING ==============
        
        @self.app.route('/agents')
        @self.login_required
        def agents():
            """Agents management page"""
            user = self.user_registry.get_user(session['user_id'])
            all_agents = self.agent_registry.list_agents()

            # Filter agents based on user access
            if not user.is_admin():
                all_agents = [a for a in all_agents if user.has_agent_access(a['agent_id'])]

            return render_template('agents.html', user=user, agents=all_agents)
        
        # ============== AGENT EXECUTION ==============
        
        @self.app.route('/execute_agent')
        @self.login_required
        def execute_agent_page():
            """Agent execution page"""
            user = self.user_registry.get_user(session['user_id'])
            all_agents = self.agent_registry.list_agents()

            # Filter agents based on user access
            if not user.is_admin():
                all_agents = [a for a in all_agents if user.has_agent_access(a['agent_id'])]

            return render_template('execute_agent.html', user=user, agents=all_agents)
        
        @self.app.route('/execute_agent/<agent_id>')
        @self.login_required
        def execute_agent_form(agent_id):
            """Agent execution form"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.has_agent_access(agent_id):
                flash('Access denied to this agent', 'danger')
                return redirect(url_for('execute_agent_page'))

            agent_info = self.agent_registry.get_agent_info(agent_id)
            if not agent_info:
                flash('Agent not found', 'danger')
                return redirect(url_for('execute_agent_page'))

            return render_template('execute_agent_form.html', user=user, agent=agent_info)
        
        @self.app.route('/api/execute_agent', methods=['POST'])
        @self.login_required
        def api_execute_agent():
            """API endpoint to execute an agent"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()
            agent_id = data.get('agent_id')
            input_data = data.get('input', {})

            if not user.has_agent_access(agent_id):
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            result = self.agent_registry.execute_agent(agent_id, input_data)

            return jsonify(result)
        
        # ============== AGENT MANAGEMENT (ADMIN) ==============
        
        @self.app.route('/create_agent')
        @self.login_required
        def create_agent_page():
            """Create agent page (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                flash('Access denied. Admin only.', 'danger')
                return redirect(url_for('agents'))

            return render_template('create_agent.html', user=user)
        
        @self.app.route('/api/create_agent', methods=['POST'])
        @self.login_required
        def api_create_agent():
            """API endpoint to create a new agent (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied. Admin only.'}), 403

            data = request.get_json()
            result = self.agent_registry.create_agent_from_json(data)

            return jsonify(result)
        
        @self.app.route('/api/agent/enable/<agent_id>', methods=['POST'])
        @self.login_required
        def api_enable_agent(agent_id):
            """API endpoint to enable an agent (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            if self.agent_registry.enable_agent(agent_id):
                return jsonify({'success': True, 'message': f'Agent {agent_id} enabled'})
            else:
                return jsonify({'success': False, 'error': 'Failed to enable agent'}), 400
        
        @self.app.route('/api/agent/disable/<agent_id>', methods=['POST'])
        @self.login_required
        def api_disable_agent(agent_id):
            """API endpoint to disable an agent (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            if self.agent_registry.disable_agent(agent_id):
                return jsonify({'success': True, 'message': f'Agent {agent_id} disabled'})
            else:
                return jsonify({'success': False, 'error': 'Failed to disable agent'}), 400
        
        @self.app.route('/api/toggle_agent', methods=['POST'])
        @self.login_required
        def api_toggle_agent():
            """API endpoint to toggle agent enable/disable (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            data = request.get_json()
            agent_id = data.get('agent_id')
            action = data.get('action')  # 'enable' or 'disable'

            if action == 'enable':
                if self.agent_registry.enable_agent(agent_id):
                    return jsonify({'success': True, 'message': f'Agent {agent_id} enabled'})
            elif action == 'disable':
                if self.agent_registry.disable_agent(agent_id):
                    return jsonify({'success': True, 'message': f'Agent {agent_id} disabled'})

            return jsonify({'success': False, 'error': 'Failed to toggle agent'}), 400
