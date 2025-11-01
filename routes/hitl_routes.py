"""
HITL Routes
Human-In-The-Loop request management and approval

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, jsonify
from routes.base_routes import BaseRoutes

class HITLRoutes(BaseRoutes):
    """HITL routes handler"""
    
    def __init__(self, app, user_registry, orchestrator, login_required):
        super().__init__()

        self.app = app
        self.user_registry = user_registry
        self.orchestrator = orchestrator
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all HITL routes"""
        
        @self.app.route('/hitl_requests')
        @self.login_required
        def hitl_requests():
            """HITL requests page"""
            user = self.user_registry.get_user(session['user_id'])

            pending_requests = self.orchestrator.get_pending_hitl_requests()

            return render_template('hitl_requests.html', user=user, requests=pending_requests)
        
        @self.app.route('/api/hitl_approve', methods=['POST'])
        @self.login_required
        def api_hitl_approve():
            """API endpoint to approve HITL request"""
            data = request.get_json()
            workflow_id = data.get('workflow_id')
            request_id = data.get('request_id')
            response = data.get('response', 'approved')

            success = self.orchestrator.approve_hitl(workflow_id, request_id, session['user_id'], response)

            return jsonify({'success': success})
        
        @self.app.route('/api/hitl_reject', methods=['POST'])
        @self.login_required
        def api_hitl_reject():
            """API endpoint to reject HITL request"""
            data = request.get_json()
            workflow_id = data.get('workflow_id')
            request_id = data.get('request_id')
            reason = data.get('reason', 'rejected')

            success = self.orchestrator.reject_hitl(workflow_id, request_id, session['user_id'], reason)

            return jsonify({'success': success})
