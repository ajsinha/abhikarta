"""
User Routes
User management for administrators

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify
from routes.base_routes import BaseRoutes

class UserRoutes(BaseRoutes):
    """User management routes handler"""
    
    def __init__(self, app, user_registry, tool_registry, agent_registry, dag_registry, login_required):
        super().__init__()

        self.app = app
        self.user_registry = user_registry
        self.tool_registry = tool_registry
        self.agent_registry = agent_registry
        self.dag_registry = dag_registry
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all user management routes"""
        
        @self.app.route('/users')
        @self.login_required
        def users():
            """Users management page (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                flash('Access denied. Admin only.', 'danger')
                return redirect(url_for('dashboard'))

            all_users = self.user_registry.get_all_users()

            return render_template('users.html', user=user, users=all_users)
        
        @self.app.route('/add_user')
        @self.login_required
        def add_user_page():
            """Add user page (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                flash('Access denied. Admin only.', 'danger')
                return redirect(url_for('dashboard'))

            # Get all tools, agents, and DAGs for the form
            all_tools = self.tool_registry.list_tools()
            all_agents = self.agent_registry.list_agents()
            all_dags = self.dag_registry.list_dags()

            return render_template('add_user.html',
                                 user=user,
                                 all_tools=all_tools,
                                 all_agents=all_agents,
                                 all_dags=all_dags)
        
        @self.app.route('/api/add_user', methods=['POST'])
        @self.login_required
        def api_add_user():
            """API endpoint to add a user (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            data = request.get_json()

            from core.user_registry import User
            new_user = User(
                user_id=data.get('user_id'),
                username=data.get('username'),
                password=data.get('password'),
                full_name=data.get('full_name', ''),
                email=data.get('email', ''),
                role=data.get('role', 'user'),
                approved_tools=data.get('approved_tools', []),
                approved_agents=data.get('approved_agents', []),
                approved_dags=data.get('approved_dags', [])
            )

            if self.user_registry.add_user(new_user):
                return jsonify({'success': True, 'message': 'User added successfully'})
            else:
                return jsonify({'success': False, 'error': 'User already exists'}), 400
        
        @self.app.route('/edit_user/<user_id>')
        @self.login_required
        def edit_user_page(user_id):
            """Edit user page (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                flash('Access denied. Admin only.', 'danger')
                return redirect(url_for('dashboard'))

            edit_user = self.user_registry.get_user(user_id)
            if not edit_user:
                flash('User not found', 'danger')
                return redirect(url_for('users'))

            # Get all tools, agents, and DAGs for the form
            all_tools = self.tool_registry.list_tools()
            all_agents = self.agent_registry.list_agents()
            all_dags = self.dag_registry.list_dags()

            return render_template('edit_user.html',
                                 user=user,
                                 edit_user=edit_user,
                                 all_tools=all_tools,
                                 all_agents=all_agents,
                                 all_dags=all_dags)
        
        @self.app.route('/api/edit_user/<user_id>', methods=['POST'])
        @self.login_required
        def api_edit_user(user_id):
            """API endpoint to edit a user (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            if user_id == 'admin':
                return jsonify({'success': False, 'error': 'Cannot edit admin user'}), 403

            data = request.get_json()

            if self.user_registry.update_user(user_id, **data):
                return jsonify({'success': True, 'message': 'User updated successfully'})
            else:
                return jsonify({'success': False, 'error': 'User not found or cannot be updated'}), 400
        
        @self.app.route('/api/delete_user/<user_id>', methods=['POST'])
        @self.login_required
        def api_delete_user(user_id):
            """API endpoint to delete a user (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            if user_id == 'admin':
                return jsonify({'success': False, 'error': 'Cannot delete admin user'}), 403

            if self.user_registry.delete_user(user_id):
                return jsonify({'success': True, 'message': 'User deleted successfully'})
            else:
                return jsonify({'success': False, 'error': 'User not found or cannot be deleted'}), 400
