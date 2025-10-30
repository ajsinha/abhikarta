"""
DAG Routes
DAG (Directed Acyclic Graph) management and listing

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify
import uuid
import json
from datetime import datetime


class DAGRoutes:
    """DAG routes handler"""
    
    def __init__(self, app, user_registry, dag_registry, orchestrator, get_db, login_required):
        self.app = app
        self.user_registry = user_registry
        self.dag_registry = dag_registry
        self.orchestrator = orchestrator
        self.get_db = get_db
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all DAG routes"""
        
        @self.app.route('/dags')
        @self.login_required
        def dags():
            """DAGs management page"""
            user = self.user_registry.get_user(session['user_id'])
            all_dags = self.dag_registry.list_dags()

            # Filter DAGs based on user access
            if not user.is_admin():
                all_dags = [d for d in all_dags if user.has_dag_access(d['dag_id'])]

            return render_template('dags.html', user=user, dags=all_dags)
        
        @self.app.route('/execute_dag/<dag_id>')
        @self.login_required
        def execute_dag(dag_id):
            """Execute DAG page"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.has_dag_access(dag_id):
                flash('Access denied to this DAG', 'danger')
                return redirect(url_for('dags'))

            dag_config = self.dag_registry.get_dag_config(dag_id)
            if not dag_config:
                flash('DAG not found', 'danger')
                return redirect(url_for('dags'))

            return render_template('execute_dag.html', user=user, dag=dag_config)
        
        @self.app.route('/api/execute_dag', methods=['POST'])
        @self.login_required
        def api_execute_dag():
            """API endpoint to execute a DAG"""
            data = request.get_json()
            dag_id = data.get('dag_id')

            user = self.user_registry.get_user(session['user_id'])
            if not user.has_dag_access(dag_id):
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            # Create graph from DAG
            graph = self.dag_registry.create_graph_from_dag(dag_id)
            if not graph:
                return jsonify({'success': False, 'error': 'DAG not found'}), 404

            # Create session
            session_id = str(uuid.uuid4())
            db = self.get_db()
            db.insert('sessions', {
                'session_id': session_id,
                'user_id': user.user_id,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'metadata': json.dumps({'dag_id': dag_id})
            })

            # Start workflow
            workflow_id = self.orchestrator.start_workflow(dag_id, session_id, user.user_id, graph)

            return jsonify({
                'success': True,
                'workflow_id': workflow_id,
                'session_id': session_id
            })
