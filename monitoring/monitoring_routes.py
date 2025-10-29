"""
Monitoring Routes for Flask Application
Add these routes to your main Flask app

© 2025-2030 Ashutosh Sinha
"""

from flask import render_template, jsonify, session, redirect, url_for
from functools import wraps
from monitoring.monitoring_service import MonitoringService

# Decorator for login required (adjust based on your auth implementation)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ========== MONITORING PAGES ==========

@app.route('/monitoring')
@login_required
def monitoring_dashboard():
    """Main monitoring dashboard"""
    return render_template('monitoring_dashboard.html')


@app.route('/monitoring/users')
@login_required
def monitoring_users():
    """User activity monitoring page"""
    return render_template('monitoring_users.html')


@app.route('/monitoring/tools')
@login_required
def monitoring_tools():
    """Tools monitoring page"""
    return render_template('monitoring_tools.html')


@app.route('/monitoring/agents')
@login_required
def monitoring_agents():
    """Agents monitoring page"""
    return render_template('monitoring_agents.html')


@app.route('/monitoring/dags')
@login_required
def monitoring_dags():
    """DAGs/Workflows monitoring page"""
    return render_template('monitoring_dags.html')


@app.route('/monitoring/planner')
@login_required
def monitoring_planner():
    """Planner monitoring page"""
    return render_template('monitoring_planner.html')


# ========== MONITORING API ENDPOINTS ==========

@app.route('/api/monitoring/dashboard')
@login_required
def api_monitoring_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        monitoring = MonitoringService()
        stats = monitoring.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/users')
@login_required
def api_monitoring_users():
    """API endpoint for user monitoring statistics"""
    try:
        monitoring = MonitoringService()
        stats = monitoring.get_user_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/tools')
@login_required
def api_monitoring_tools():
    """API endpoint for tools monitoring statistics"""
    try:
        monitoring = MonitoringService()
        stats = monitoring.get_tools_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/agents')
@login_required
def api_monitoring_agents():
    """API endpoint for agents monitoring statistics"""
    try:
        monitoring = MonitoringService()
        stats = monitoring.get_agents_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/dags')
@login_required
def api_monitoring_dags():
    """API endpoint for DAGs monitoring statistics"""
    try:
        monitoring = MonitoringService()
        stats = monitoring.get_dags_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/planner')
@login_required
def api_monitoring_planner():
    """API endpoint for planner monitoring statistics"""
    try:
        monitoring = MonitoringService()
        stats = monitoring.get_planner_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500