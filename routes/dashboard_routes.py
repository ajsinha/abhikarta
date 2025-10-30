"""
Dashboard Routes
Main dashboard with statistics and overview

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template


class DashboardRoutes:
    """Dashboard routes handler"""
    
    def __init__(self, app, user_registry, orchestrator, tool_registry, get_db, login_required):
        self.app = app
        self.user_registry = user_registry
        self.orchestrator = orchestrator
        self.tool_registry = tool_registry
        self.get_db = get_db
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all dashboard routes"""
        
        @self.app.route('/dashboard')
        @self.login_required
        def dashboard():
            """Dashboard page"""
            user = self.user_registry.get_user(session['user_id'])
            
            # Get statistics
            db = self.get_db()
            
            total_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows")['count']
            running_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows WHERE status = 'running'")['count']
            completed_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows WHERE status = 'completed'")['count']
            failed_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows WHERE status = 'failed'")['count']
            
            # Get recent workflows
            recent_workflows = db.fetchall(
                "SELECT * FROM workflows ORDER BY created_at DESC LIMIT 10"
            )
            
            # Get pending HITL requests
            pending_hitl = self.orchestrator.get_pending_hitl_requests()
            
            # Get MCP server status
            mcp_servers = self.tool_registry.get_mcp_servers_status()

            return render_template('dashboard.html',
                                 user=user,
                                 total_workflows=total_workflows,
                                 running_workflows=running_workflows,
                                 completed_workflows=completed_workflows,
                                 failed_workflows=failed_workflows,
                                 recent_workflows=recent_workflows,
                                 pending_hitl=len(pending_hitl),
                                 mcp_servers=mcp_servers)
