"""
Monitoring Routes
System monitoring, statistics, and analytics

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import render_template, jsonify


class MonitoringRoutes:
    """Monitoring routes handler"""
    
    def __init__(self, app, login_required, admin_required):
        self.app = app
        self.login_required = login_required
        self.admin_required = admin_required
        self.register_routes()
    
    def register_routes(self):
        """Register all monitoring routes"""
        
        # ============== MONITORING PAGES ==============
        
        @self.app.route('/monitoring')
        @self.login_required
        def monitoring_dashboard():
            """Main monitoring dashboard"""
            return render_template('monitoring_dashboard.html')
        
        @self.app.route('/monitoring/users')
        @self.login_required
        def monitoring_users():
            """User activity monitoring page"""
            return render_template('monitoring_users.html')
        
        @self.app.route('/monitoring/tools')
        @self.login_required
        def monitoring_tools():
            """Tools monitoring page"""
            return render_template('monitoring_tools.html')
        
        @self.app.route('/monitoring/agents')
        @self.login_required
        def monitoring_agents():
            """Agents monitoring page"""
            return render_template('monitoring_agents.html')


        @self.app.route('/monitoring/dags')
        @self.login_required
        def monitoring_dags():
            """DAGs/Workflows monitoring page"""
            return render_template('monitoring_dags.html')
        
        @self.app.route('/monitoring/planner')
        @self.login_required
        def monitoring_planner():
            """Planner monitoring page"""
            return render_template('monitoring_planner.html')
        
        # ============== MONITORING API ENDPOINTS ==============
        
        @self.app.route('/api/monitoring/dashboard')
        @self.login_required
        def api_monitoring_dashboard_stats():
            """API endpoint for dashboard statistics"""
            from monitoring.monitoring_service import MonitoringService
            
            try:
                monitoring = MonitoringService()
                stats = monitoring.get_dashboard_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/users')
        @self.login_required
        def api_monitoring_users():
            """API endpoint for user monitoring statistics"""
            from monitoring.monitoring_service import MonitoringService
            
            try:
                monitoring = MonitoringService()
                stats = monitoring.get_user_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/tools')
        @self.login_required
        def api_monitoring_tools():
            """API endpoint for tools monitoring statistics"""
            from monitoring.monitoring_service import MonitoringService
            
            try:
                monitoring = MonitoringService()
                stats = monitoring.get_tools_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/agents')
        @self.login_required
        def api_monitoring_agents():
            """API endpoint for agents monitoring statistics"""
            from monitoring.monitoring_service import MonitoringService
            
            try:
                monitoring = MonitoringService()
                stats = monitoring.get_agents_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/dags')
        @self.login_required
        def api_monitoring_dags():
            """API endpoint for DAGs monitoring statistics"""
            from monitoring.monitoring_service import MonitoringService
            
            try:
                monitoring = MonitoringService()
                stats = monitoring.get_dags_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/planner')
        @self.login_required
        def api_monitoring_planner():
            """API endpoint for planner monitoring statistics"""
            from monitoring.monitoring_service import MonitoringService
            
            try:
                monitoring = MonitoringService()
                stats = monitoring.get_planner_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
