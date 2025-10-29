"""
Main Flask Application for Abhikarta
Web interface for multi-agent orchestration system

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
import json
import uuid
from datetime import datetime, timedelta
from functools import wraps

# Import core modules
from core.properties_configurator import PropertiesConfigurator
from core.database import initialize_db, get_db
from core.user_registry import UserRegistry
from agents.agent_registry import AgentRegistry
from tools.tool_registry import ToolRegistry
from workflows.dag_registry import DAGRegistry
from workflows.orchestrator import WorkflowOrchestrator
from workflows.planner import Planner, initialize_planner_tables


# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load configuration
props = PropertiesConfigurator()
props.load_properties('application.properties')

# Initialize database
initialize_db(db_type='sqlite', db_path='data/abhikarta.db')
initialize_planner_tables()

# Initialize registries
user_registry = UserRegistry()
agent_registry = AgentRegistry()
tool_registry = ToolRegistry()
dag_registry = DAGRegistry()
orchestrator = WorkflowOrchestrator()

# Initialize planner
llm_provider = props.get('llm.default.provider', 'mock')
planner = Planner(llm_provider=llm_provider)


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Routes
@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = user_registry.authenticate(username, password)
        if user:
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role
            
            # Update last login
            db = get_db()
            db.execute(
                "INSERT OR REPLACE INTO users (user_id, username, full_name, email, role, last_login) VALUES (?, ?, ?, ?, ?, ?)",
                (user.user_id, user.username, user.full_name, user.email, user.role, datetime.now().isoformat())
            )
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    user = user_registry.get_user(session['user_id'])
    
    # Get statistics
    db = get_db()
    
    total_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows")['count']
    running_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows WHERE status = 'running'")['count']
    completed_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows WHERE status = 'completed'")['count']
    failed_workflows = db.fetchone("SELECT COUNT(*) as count FROM workflows WHERE status = 'failed'")['count']
    
    # Get recent workflows
    recent_workflows = db.fetchall(
        "SELECT * FROM workflows ORDER BY created_at DESC LIMIT 10"
    )
    
    # Get pending HITL requests
    pending_hitl = orchestrator.get_pending_hitl_requests()
    
    # Get MCP server status
    mcp_servers = tool_registry.get_mcp_servers_status()

    return render_template('dashboard.html',
                         user=user,
                         total_workflows=total_workflows,
                         running_workflows=running_workflows,
                         completed_workflows=completed_workflows,
                         failed_workflows=failed_workflows,
                         recent_workflows=recent_workflows,
                         pending_hitl=len(pending_hitl),
                         mcp_servers=mcp_servers)


@app.route('/agents')
@login_required
def agents():
    """Agents management page"""
    user = user_registry.get_user(session['user_id'])
    all_agents = agent_registry.list_agents()

    # Filter agents based on user access
    if not user.is_admin():
        all_agents = [a for a in all_agents if user.has_agent_access(a['agent_id'])]

    return render_template('agents.html', user=user, agents=all_agents)


@app.route('/tools')
@login_required
def tools():
    """Tools management page"""
    user = user_registry.get_user(session['user_id'])
    all_tools = tool_registry.list_tools()

    # Filter tools based on user access
    if not user.is_admin():
        all_tools = [t for t in all_tools if user.has_tool_access(t['tool_name'])]

    return render_template('tools.html', user=user, tools=all_tools)


@app.route('/dags')
@login_required
def dags():
    """DAGs management page"""
    user = user_registry.get_user(session['user_id'])
    all_dags = dag_registry.list_dags()

    # Filter DAGs based on user access
    if not user.is_admin():
        all_dags = [d for d in all_dags if user.has_dag_access(d['dag_id'])]

    return render_template('dags.html', user=user, dags=all_dags)


@app.route('/workflows')
@login_required
def workflows():
    """Workflows page"""
    user = user_registry.get_user(session['user_id'])
    db = get_db()

    # Get all workflows
    all_workflows = db.fetchall("SELECT * FROM workflows ORDER BY created_at DESC")

    return render_template('workflows.html', user=user, workflows=all_workflows)


@app.route('/workflow/<workflow_id>')
@login_required
def workflow_detail(workflow_id):
    """Workflow detail page"""
    user = user_registry.get_user(session['user_id'])

    status = orchestrator.get_workflow_status(workflow_id)
    if not status:
        flash('Workflow not found', 'danger')
        return redirect(url_for('workflows'))

    # Get workflow events
    db = get_db()
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


@app.route('/execute_dag/<dag_id>')
@login_required
def execute_dag(dag_id):
    """Execute DAG page"""
    user = user_registry.get_user(session['user_id'])

    if not user.has_dag_access(dag_id):
        flash('Access denied to this DAG', 'danger')
        return redirect(url_for('dags'))

    dag_config = dag_registry.get_dag_config(dag_id)
    if not dag_config:
        flash('DAG not found', 'danger')
        return redirect(url_for('dags'))

    return render_template('execute_dag.html', user=user, dag=dag_config)


@app.route('/api/execute_dag', methods=['POST'])
@login_required
def api_execute_dag():
    """API endpoint to execute a DAG"""
    data = request.get_json()
    dag_id = data.get('dag_id')

    user = user_registry.get_user(session['user_id'])
    if not user.has_dag_access(dag_id):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    # Create graph from DAG
    graph = dag_registry.create_graph_from_dag(dag_id)
    if not graph:
        return jsonify({'success': False, 'error': 'DAG not found'}), 404

    # Create session
    session_id = str(uuid.uuid4())
    db = get_db()
    db.insert('sessions', {
        'session_id': session_id,
        'user_id': user.user_id,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'metadata': json.dumps({'dag_id': dag_id})
    })

    # Start workflow
    workflow_id = orchestrator.start_workflow(dag_id, session_id, user.user_id, graph)

    return jsonify({
        'success': True,
        'workflow_id': workflow_id,
        'session_id': session_id
    })


@app.route('/api/workflow_status/<workflow_id>')
@login_required
def api_workflow_status(workflow_id):
    """API endpoint to get workflow status"""
    status = orchestrator.get_workflow_status(workflow_id)
    if not status:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404

    return jsonify({
        'success': True,
        'workflow': status['workflow'],
        'nodes': status['nodes']
    })


@app.route('/hitl_requests')
@login_required
def hitl_requests():
    """HITL requests page"""
    user = user_registry.get_user(session['user_id'])

    pending_requests = orchestrator.get_pending_hitl_requests()

    return render_template('hitl_requests.html', user=user, requests=pending_requests)


@app.route('/api/hitl_approve', methods=['POST'])
@login_required
def api_hitl_approve():
    """API endpoint to approve HITL request"""
    data = request.get_json()
    workflow_id = data.get('workflow_id')
    request_id = data.get('request_id')
    response = data.get('response', 'approved')

    success = orchestrator.approve_hitl(workflow_id, request_id, session['user_id'], response)

    return jsonify({'success': success})


@app.route('/api/hitl_reject', methods=['POST'])
@login_required
def api_hitl_reject():
    """API endpoint to reject HITL request"""
    data = request.get_json()
    workflow_id = data.get('workflow_id')
    request_id = data.get('request_id')
    reason = data.get('reason', 'rejected')

    success = orchestrator.reject_hitl(workflow_id, request_id, session['user_id'], reason)

    return jsonify({'success': success})


@app.route('/users')
@login_required
def users():
    """Users management page (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard'))

    all_users = user_registry.get_all_users()

    return render_template('users.html', user=user, users=all_users)


@app.route('/api/reload_config', methods=['POST'])
@login_required
def api_reload_config():
    """API endpoint to reload configuration (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        user_registry.reload()
        agent_registry.reload()
        tool_registry.reload()
        dag_registry.reload()

        return jsonify({'success': True, 'message': 'Configuration reloaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== PLANNER ROUTES ==============

@app.route('/planner')
@login_required
def planner_page():
    """Planner chat interface"""
    user = user_registry.get_user(session['user_id'])

    # Get recent conversations
    conversations = planner.get_conversation_history(user.user_id, limit=20)

    # Get user's pending plans
    plans = planner.get_user_plans(user.user_id)
    pending_plans = [p for p in plans if p['status'] == 'pending_approval']

    return render_template('planner.html',
                         user=user,
                         conversations=conversations,
                         pending_plans=pending_plans)


@app.route('/create_plan')
@login_required
def create_plan_page():
    """Create plan page"""
    user = user_registry.get_user(session['user_id'])
    return render_template('create_plan.html', user=user)


@app.route('/api/planner/chat', methods=['POST'])
@login_required
def api_planner_chat():
    """API endpoint for planner chat"""
    data = request.get_json()
    message = data.get('message', '')
    conversation_history = data.get('history', [])

    response = planner.chat(session['user_id'], message, conversation_history)

    return jsonify({
        'success': True,
        'response': response['response'],
        'timestamp': response['timestamp']
    })


@app.route('/api/planner/create_plan', methods=['POST'])
@login_required
def api_planner_create_plan():
    """API endpoint to create a plan from request"""
    user = user_registry.get_user(session['user_id'])
    data = request.get_json()
    request_text = data.get('request', '')

    # Get available tools and agents for this user
    all_tools = tool_registry.list_tools()
    all_agents = agent_registry.list_agents()

    available_tools = [t['tool_name'] for t in all_tools if user.has_tool_access(t['tool_name'])]
    available_agents = [a['agent_id'] for a in all_agents if user.has_agent_access(a['agent_id'])]

    result = planner.create_plan_from_request(
        user.user_id,
        request_text,
        available_tools,
        available_agents
    )

    return jsonify({
        'success': True,
        'plan_id': result['plan_id'],
        'plan': result['plan'],
        'message': result['message']
    })


@app.route('/plan/<plan_id>')
@login_required
def plan_detail(plan_id):
    """Plan review page"""
    user = user_registry.get_user(session['user_id'])

    plan_data = planner.get_plan(plan_id)
    if not plan_data:
        flash('Plan not found', 'danger')
        return redirect(url_for('planner_page'))

    # Check if user owns this plan or is admin
    if plan_data['user_id'] != user.user_id and not user.is_admin():
        flash('Access denied', 'danger')
        return redirect(url_for('planner_page'))

    return render_template('plan_detail.html', user=user, plan=plan_data)


@app.route('/api/plan/approve/<plan_id>', methods=['POST'])
@login_required
def api_approve_plan(plan_id):
    """Approve a plan"""
    user = user_registry.get_user(session['user_id'])

    plan_data = planner.get_plan(plan_id)
    if not plan_data or (plan_data['user_id'] != user.user_id and not user.is_admin()):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    planner.approve_plan(plan_id)

    return jsonify({'success': True, 'message': 'Plan approved'})


@app.route('/api/plan/reject/<plan_id>', methods=['POST'])
@login_required
def api_reject_plan(plan_id):
    """Reject a plan"""
    user = user_registry.get_user(session['user_id'])
    data = request.get_json()
    reason = data.get('reason', '')

    plan_data = planner.get_plan(plan_id)
    if not plan_data or (plan_data['user_id'] != user.user_id and not user.is_admin()):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    planner.reject_plan(plan_id, reason)

    return jsonify({'success': True, 'message': 'Plan rejected'})


@app.route('/api/plan/execute/<plan_id>', methods=['POST'])
@login_required
def api_execute_plan(plan_id):
    """Execute an approved plan"""
    user = user_registry.get_user(session['user_id'])

    plan_data = planner.get_plan(plan_id)
    if not plan_data:
        return jsonify({'success': False, 'error': 'Plan not found'}), 404

    if plan_data['status'] != 'approved':
        return jsonify({'success': False, 'error': 'Plan must be approved first'}), 400

    # Create graph from plan
    plan = plan_data['plan']
    graph = dag_registry.create_graph_from_dag(plan['dag_id'])

    if not graph:
        # Create graph from plan definition
        from core.graph import Graph, Node, Edge
        graph = Graph(
            graph_id=plan['dag_id'],
            name=plan['name'],
            description=plan['description']
        )

        for node_config in plan['nodes']:
            node = Node(
                node_id=node_config['node_id'],
                node_type=node_config['node_type'],
                agent_id=node_config.get('agent_id'),
                config=node_config.get('config', {})
            )
            graph.add_node(node)

        for node_config in plan['nodes']:
            node_id = node_config['node_id']
            for dep in node_config.get('dependencies', []):
                edge = Edge(from_node=dep, to_node=node_id)
                graph.add_edge(edge)

        graph.start_nodes = plan.get('start_nodes', [])

    # Create session
    session_id = str(uuid.uuid4())
    db = get_db()
    db.insert('sessions', {
        'session_id': session_id,
        'user_id': user.user_id,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'metadata': json.dumps({'plan_id': plan_id})
    })

    # Start workflow
    workflow_id = orchestrator.start_workflow(plan['dag_id'], session_id, user.user_id, graph)

    # Update plan status
    db.update('plans', {'status': 'executed'}, 'plan_id = ?', (plan_id,))

    return jsonify({
        'success': True,
        'workflow_id': workflow_id,
        'message': 'Plan execution started'
    })


# ============== TOOL EXECUTION ROUTES ==============

@app.route('/execute_tool')
@login_required
def execute_tool_page():
    """Tool execution page"""
    user = user_registry.get_user(session['user_id'])
    all_tools = tool_registry.list_tools()

    # Filter tools based on user access
    if not user.is_admin():
        all_tools = [t for t in all_tools if user.has_tool_access(t['tool_name'])]

    return render_template('execute_tool.html', user=user, tools=all_tools)


@app.route('/execute_tool/<tool_name>')
@login_required
def execute_tool_form(tool_name):
    """Tool execution form"""
    user = user_registry.get_user(session['user_id'])

    if not user.has_tool_access(tool_name):
        flash('Access denied to this tool', 'danger')
        return redirect(url_for('execute_tool_page'))

    tool_info = tool_registry.get_tool_info(tool_name)
    if not tool_info:
        flash('Tool not found', 'danger')
        return redirect(url_for('execute_tool_page'))

    return render_template('execute_tool_form.html', user=user, tool=tool_info)


@app.route('/api/execute_tool', methods=['POST'])
@login_required
def api_execute_tool():
    """API endpoint to execute a tool"""
    user = user_registry.get_user(session['user_id'])
    data = request.get_json()
    tool_name = data.get('tool_name')
    params = data.get('params', {})

    if not user.has_tool_access(tool_name):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    result = tool_registry.execute_tool(tool_name, **params)

    return jsonify(result)


# ============== AGENT EXECUTION ROUTES ==============

@app.route('/execute_agent')
@login_required
def execute_agent_page():
    """Agent execution page"""
    user = user_registry.get_user(session['user_id'])
    all_agents = agent_registry.list_agents()

    # Filter agents based on user access
    if not user.is_admin():
        all_agents = [a for a in all_agents if user.has_agent_access(a['agent_id'])]

    return render_template('execute_agent.html', user=user, agents=all_agents)


@app.route('/execute_agent/<agent_id>')
@login_required
def execute_agent_form(agent_id):
    """Agent execution form"""
    user = user_registry.get_user(session['user_id'])

    if not user.has_agent_access(agent_id):
        flash('Access denied to this agent', 'danger')
        return redirect(url_for('execute_agent_page'))

    agent_info = agent_registry.get_agent_info(agent_id)
    if not agent_info:
        flash('Agent not found', 'danger')
        return redirect(url_for('execute_agent_page'))

    return render_template('execute_agent_form.html', user=user, agent=agent_info)


@app.route('/api/execute_agent', methods=['POST'])
@login_required
def api_execute_agent():
    """API endpoint to execute an agent"""
    user = user_registry.get_user(session['user_id'])
    data = request.get_json()
    agent_id = data.get('agent_id')
    input_data = data.get('input', {})

    if not user.has_agent_access(agent_id):
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    result = agent_registry.execute_agent(agent_id, input_data)

    return jsonify(result)


# ============== AGENT MANAGEMENT ROUTES ==============

@app.route('/create_agent')
@login_required
def create_agent_page():
    """Create agent page (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('agents'))

    return render_template('create_agent.html', user=user)


@app.route('/api/create_agent', methods=['POST'])
@login_required
def api_create_agent():
    """API endpoint to create a new agent (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied. Admin only.'}), 403

    data = request.get_json()
    result = agent_registry.create_agent_from_json(data)

    return jsonify(result)


@app.route('/api/agent/enable/<agent_id>', methods=['POST'])
@login_required
def api_enable_agent(agent_id):
    """API endpoint to enable an agent (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if agent_registry.enable_agent(agent_id):
        return jsonify({'success': True, 'message': f'Agent {agent_id} enabled'})
    else:
        return jsonify({'success': False, 'error': 'Failed to enable agent'}), 400


@app.route('/api/agent/disable/<agent_id>', methods=['POST'])
@login_required
def api_disable_agent(agent_id):
    """API endpoint to disable an agent (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if agent_registry.disable_agent(agent_id):
        return jsonify({'success': True, 'message': f'Agent {agent_id} disabled'})
    else:
        return jsonify({'success': False, 'error': 'Failed to disable agent'}), 400


@app.route('/api/toggle_agent', methods=['POST'])
@login_required
def api_toggle_agent():
    """API endpoint to toggle agent enable/disable (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()
    agent_id = data.get('agent_id')
    action = data.get('action')  # 'enable' or 'disable'

    if action == 'enable':
        if agent_registry.enable_agent(agent_id):
            return jsonify({'success': True, 'message': f'Agent {agent_id} enabled'})
    elif action == 'disable':
        if agent_registry.disable_agent(agent_id):
            return jsonify({'success': True, 'message': f'Agent {agent_id} disabled'})

    return jsonify({'success': False, 'error': 'Failed to toggle agent'}), 400


# ============== TOOL MANAGEMENT ROUTES ==============

@app.route('/create_tool')
@login_required
def create_tool_page():
    """Create tool page (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('tools'))

    return render_template('create_tool.html', user=user)


@app.route('/api/create_tool', methods=['POST'])
@login_required
def api_create_tool():
    """API endpoint to create a new tool (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied. Admin only.'}), 403

    data = request.get_json()
    result = tool_registry.create_tool_from_json(data)

    return jsonify(result)


@app.route('/api/tool/enable/<tool_name>', methods=['POST'])
@login_required
def api_enable_tool(tool_name):
    """API endpoint to enable a tool (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if tool_registry.enable_tool(tool_name):
        return jsonify({'success': True, 'message': f'Tool {tool_name} enabled'})
    else:
        return jsonify({'success': False, 'error': 'Failed to enable tool'}), 400


@app.route('/api/tool/disable/<tool_name>', methods=['POST'])
@login_required
def api_disable_tool(tool_name):
    """API endpoint to disable a tool (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if tool_registry.disable_tool(tool_name):
        return jsonify({'success': True, 'message': f'Tool {tool_name} disabled'})
    else:
        return jsonify({'success': False, 'error': 'Failed to disable tool'}), 400


@app.route('/api/toggle_tool', methods=['POST'])
@login_required
def api_toggle_tool():
    """API endpoint to toggle tool enable/disable (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()
    tool_name = data.get('tool_name')
    action = data.get('action')  # 'enable' or 'disable'

    if action == 'enable':
        if tool_registry.enable_tool(tool_name):
            return jsonify({'success': True, 'message': f'Tool {tool_name} enabled'})
    elif action == 'disable':
        if tool_registry.disable_tool(tool_name):
            return jsonify({'success': True, 'message': f'Tool {tool_name} disabled'})

    return jsonify({'success': False, 'error': 'Failed to toggle tool'}), 400


# ============== USER MANAGEMENT ROUTES ==============

@app.route('/add_user')
@login_required
def add_user_page():
    """Add user page (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard'))

    # Get all tools, agents, and DAGs for the form
    all_tools = tool_registry.list_tools()
    all_agents = agent_registry.list_agents()
    all_dags = dag_registry.list_dags()

    return render_template('add_user.html',
                         user=user,
                         all_tools=all_tools,
                         all_agents=all_agents,
                         all_dags=all_dags)


@app.route('/api/add_user', methods=['POST'])
@login_required
def api_add_user():
    """API endpoint to add a user (admin only)"""
    user = user_registry.get_user(session['user_id'])

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

    if user_registry.add_user(new_user):
        return jsonify({'success': True, 'message': 'User added successfully'})
    else:
        return jsonify({'success': False, 'error': 'User already exists'}), 400


@app.route('/edit_user/<user_id>')
@login_required
def edit_user_page(user_id):
    """Edit user page (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('dashboard'))

    edit_user = user_registry.get_user(user_id)
    if not edit_user:
        flash('User not found', 'danger')
        return redirect(url_for('users'))

    # Get all tools, agents, and DAGs for the form
    all_tools = tool_registry.list_tools()
    all_agents = agent_registry.list_agents()
    all_dags = dag_registry.list_dags()

    return render_template('edit_user.html',
                         user=user,
                         edit_user=edit_user,
                         all_tools=all_tools,
                         all_agents=all_agents,
                         all_dags=all_dags)


@app.route('/api/edit_user/<user_id>', methods=['POST'])
@login_required
def api_edit_user(user_id):
    """API endpoint to edit a user (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if user_id == 'admin':
        return jsonify({'success': False, 'error': 'Cannot edit admin user'}), 403

    data = request.get_json()

    if user_registry.update_user(user_id, **data):
        return jsonify({'success': True, 'message': 'User updated successfully'})
    else:
        return jsonify({'success': False, 'error': 'User not found or cannot be updated'}), 400


@app.route('/api/delete_user/<user_id>', methods=['POST'])
@login_required
def api_delete_user(user_id):
    """API endpoint to delete a user (admin only)"""
    user = user_registry.get_user(session['user_id'])

    if not user.is_admin():
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    if user_id == 'admin':
        return jsonify({'success': False, 'error': 'Cannot delete admin user'}), 403

    if user_registry.delete_user(user_id):
        return jsonify({'success': True, 'message': 'User deleted successfully'})
    else:
        return jsonify({'success': False, 'error': 'User not found or cannot be deleted'}), 400

from monitoring.monitoring_service import MonitoringService
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

if __name__ == '__main__':
    host = props.get('server.host', '0.0.0.0')
    port = props.get_int('server.port', 5001)
    debug = props.get_bool('server.debug', True)

    app.run(host=host, port=port, debug=debug, threaded=True)