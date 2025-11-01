"""
Configuration Routes
System configuration reload and management

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, jsonify
from routes.base_routes import BaseRoutes

class ConfigRoutes(BaseRoutes):
    """Configuration routes handler"""
    
    def __init__(self, app, user_registry, agent_registry, tool_registry, dag_registry, login_required):
        super().__init__()

        self.app = app
        self.user_registry = user_registry
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.dag_registry = dag_registry
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all configuration routes"""
        
        @self.app.route('/api/reload_config', methods=['POST'])
        @self.login_required
        def api_reload_config():
            """API endpoint to reload configuration (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            try:
                self.user_registry.reload()
                self.agent_registry.reload()
                self.tool_registry.reload()
                self.dag_registry.reload()

                return jsonify({'success': True, 'message': 'Configuration reloaded successfully'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
