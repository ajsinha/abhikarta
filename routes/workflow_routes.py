"""
Workflow Routes
Workflow listing, monitoring, and status tracking

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify


class WorkflowRoutes:
    """Workflow routes handler"""
    
    def __init__(self, app, user_registry, orchestrator, get_db, login_required):
        self.app = app
        self.user_registry = user_registry
        self.orchestrator = orchestrator
        self.get_db = get_db
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all workflow routes"""
        
        @self.app.route('/workflows')
        @self.login_required
        def workflows():
            """Workflows page"""
            user = self.user_registry.get_user(session['user_id'])
            db = self.get_db()

            # Get all workflows
            all_workflows = db.fetchall("SELECT * FROM workflows ORDER BY created_at DESC")

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

            # Get workflow events
            db = self.get_db()
            events = db.fetchall(
                "SELECT * FROM workflow_events WHERE workflow_id = ? ORDER BY created_at DESC",
                (workflow_id,)
            )

            # Get HITL requests
            hitl_requests = db.fetchall(
                "SELECT * FROM hitl_requests WHERE workflow_id = ?",
                (workflow_id,)
            )

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
