"""
Dashboard Routes (Refactored)
Main dashboard with statistics and overview

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template

class DashboardRoutes:
    """Dashboard routes handler"""

    def __init__(self, app, user_registry, orchestrator, tool_registry, db_handler, login_required):
        """
        Initialize dashboard routes

        Args:
            app: Flask application instance
            user_registry: User registry instance
            orchestrator: Workflow orchestrator instance
            tool_registry: Tool registry instance
            db_handler: DatabaseCallHandler instance
            login_required: Login required decorator
        """
        self.app = app
        self.user_registry = user_registry
        self.orchestrator = orchestrator
        self.tool_registry = tool_registry
        self.db_handler = db_handler
        self.login_required = login_required
        self.register_routes()

    def register_routes(self):
        """Register all dashboard routes"""

        @self.app.route('/dashboard')
        @self.login_required
        def dashboard():
            """Dashboard page"""
            user = self.user_registry.get_user(session['user_id'])

            # Get statistics using the handler
            stats = self.db_handler.get_workflow_statistics()

            total_workflows = stats['total']
            running_workflows = stats['running']
            completed_workflows = stats['completed']
            failed_workflows = stats['failed']

            # Get recent workflows using the handler
            recent_workflows = self.db_handler.get_recent_workflows(limit=10)

            # Get pending HITL requests using the handler
            pending_hitl_requests = self.db_handler.get_pending_hitl_requests()

            # Get MCP server status
            mcp_servers = self.tool_registry.get_mcp_servers_status()

            return render_template('dashboard.html',
                                 user=user,
                                 total_workflows=total_workflows,
                                 running_workflows=running_workflows,
                                 completed_workflows=completed_workflows,
                                 failed_workflows=failed_workflows,
                                 recent_workflows=recent_workflows,
                                 pending_hitl=len(pending_hitl_requests),
                                 mcp_servers=mcp_servers)