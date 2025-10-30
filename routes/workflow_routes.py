"""
Workflow Routes (Refactored)
Workflow listing, monitoring, and status tracking

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify


class WorkflowRoutes:
    """Workflow routes handler"""

    def __init__(self, app, user_registry, orchestrator, db_handler, login_required):
        """
        Initialize workflow routes

        Args:
            app: Flask application instance
            user_registry: User registry instance
            orchestrator: Workflow orchestrator instance
            db_handler: DatabaseCallHandler instance
            login_required: Login required decorator
        """
        self.app = app
        self.user_registry = user_registry
        self.orchestrator = orchestrator
        self.db_handler = db_handler
        self.login_required = login_required
        self.register_routes()

    def register_routes(self):
        """Register all workflow routes"""

        @self.app.route('/workflows')
        @self.login_required
        def workflows():
            """Workflows page"""
            user = self.user_registry.get_user(session['user_id'])

            # Get all workflows using the handler
            all_workflows = self.db_handler.get_all_workflows()

            return render_template('workflows.html', user=user, workflows=all_workflows)

        @self.app.route('/workflow/<workflow_id>')
        @self.login_required
        def workflow_detail(workflow_id):
            """Workflow detail page"""
            user = self.user_registry.get_user(session['user_id'])

            status = self.orchestrator.get_workflow_status(workflow_id)
            if not status:
                flash('Workflow not found', 'danger')
                return redirect(url_for('workflows'))

            # Get workflow events using the handler
            events = self.db_handler.get_workflow_events(workflow_id)

            # Get HITL requests using the handler
            hitl_requests = self.db_handler.get_hitl_requests(workflow_id)

            return render_template('workflow_detail.html',
                                 user=user,
                                 workflow=status['workflow'],
                                 nodes=status['nodes'],
                                 events=events,
                                 hitl_requests=hitl_requests)

        @self.app.route('/api/workflow_status/<workflow_id>')
        @self.login_required
        def api_workflow_status(workflow_id):
            """API endpoint to get workflow status"""
            status = self.orchestrator.get_workflow_status(workflow_id)
            if not status:
                return jsonify({'success': False, 'error': 'Workflow not found'}), 404

            return jsonify({
                'success': True,
                'workflow': status['workflow'],
                'nodes': status['nodes']
            })