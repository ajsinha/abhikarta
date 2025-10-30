"""
Main Flask Application for Abhikarta
Web interface for multi-agent orchestration system

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import Flask
import os

# Import core modules
from core.properties_configurator import PropertiesConfigurator
from db.database import initialize_db, get_db
from db.database_call_handler import get_database_handler
from core.user_registry import UserRegistry
from agents.agent_registry import AgentRegistry
from tools.tool_registry import ToolRegistry
from workflows.dag.dag_registry import DAGRegistry
from workflows.dag.orchestrator import WorkflowOrchestrator
from workflows.dag.planner import Planner, initialize_planner_tables

# Import route classes
from routes.auth_routes import AuthRoutes
from routes.dashboard_routes import DashboardRoutes
from routes.agent_routes import AgentRoutes
from routes.tool_routes import ToolRoutes
from routes.dag_routes import DAGRoutes
from routes.workflow_routes import WorkflowRoutes
from routes.hitl_routes import HITLRoutes
from routes.planner_routes import PlannerRoutes
from routes.lgraph_planner_routes import LGraphPlannerRoutes
from routes.user_routes import UserRoutes
from routes.monitoring_routes import MonitoringRoutes
from routes.config_routes import ConfigRoutes


class AbhikartaApp:
    """
    Abhikarta Application Class
    Encapsulates the Flask application and all its dependencies
    """

    def __init__(self, config_file='application.properties'):
        """
        Initialize the Abhikarta application

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.app = None
        self.props = None
        self.user_registry = None
        self.agent_registry = None
        self.tool_registry = None
        self.dag_registry = None
        self.orchestrator = None
        self.planner = None

        # Initialize the application
        self._initialize_app()
        self._load_configuration()
        self._initialize_database()
        self._initialize_registries()
        self._initialize_routes()

    def _initialize_app(self):
        """Initialize the Flask application"""
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)

    def _load_configuration(self):
        """Load application configuration"""
        self.props = PropertiesConfigurator()
        self.props.load_properties(self.config_file)

    def _initialize_database(self):
        """Initialize database and tables"""
        db_type = self.props.get('db.type', 'sqlite')
        db_path = self.props.get('db.path', 'data/abhikarta.db')

        initialize_db(db_type=db_type, db_path=db_path)
        initialize_planner_tables()

    def _initialize_registries(self):
        """Initialize all registries and core services"""
        self.user_registry = UserRegistry()
        self.agent_registry = AgentRegistry()
        self.tool_registry = ToolRegistry()
        self.dag_registry = DAGRegistry()
        self.orchestrator = WorkflowOrchestrator()

        # Initialize planner
        llm_provider = self.props.get('llm.default.provider', 'mock')
        self.planner = Planner(llm_provider=llm_provider)

    def _initialize_routes(self):
        """Initialize all route classes"""
        # Initialize authentication routes first (to get login_required decorator)
        auth_routes = AuthRoutes(self.app, self.user_registry, get_db)
        login_required = auth_routes.login_required
        admin_required = auth_routes.admin_required

        # Initialize all other route classes
        dashboard_routes = DashboardRoutes(
            self.app, self.user_registry, self.orchestrator,
            self.tool_registry, get_database_handler(), login_required
        )

        agent_routes = AgentRoutes(
            self.app, self.user_registry, self.agent_registry, login_required
        )

        tool_routes = ToolRoutes(
            self.app, self.user_registry, self.tool_registry, login_required
        )

        dag_routes = DAGRoutes(
            self.app, self.user_registry, self.dag_registry,
            self.orchestrator, get_db, login_required
        )

        workflow_routes = WorkflowRoutes(
            self.app, self.user_registry, self.orchestrator, get_database_handler(), login_required
        )

        hitl_routes = HITLRoutes(
            self.app, self.user_registry, self.orchestrator, login_required
        )

        planner_routes = PlannerRoutes(
            self.app, self.user_registry, self.planner, self.tool_registry,
            self.agent_registry, self.dag_registry, self.orchestrator,
            get_db, login_required
        )

        lgraph_planner_routes = LGraphPlannerRoutes(
            self.app, self.user_registry, get_db, login_required
        )

        user_routes = UserRoutes(
            self.app, self.user_registry, self.tool_registry,
            self.agent_registry, self.dag_registry, login_required
        )

        monitoring_routes = MonitoringRoutes(self.app, login_required, admin_required)

        config_routes = ConfigRoutes(
            self.app, self.user_registry, self.agent_registry,
            self.tool_registry, self.dag_registry, login_required
        )

    def get_app(self):
        """
        Get the Flask application instance

        Returns:
            Flask application instance
        """
        return self.app

    def get_config(self):
        """
        Get the configuration properties

        Returns:
            PropertiesConfigurator instance
        """
        return self.props

    def run(self, host=None, port=None, debug=None, ssl_context=None):
        """
        Run the Flask application

        Args:
            host: Host to bind to (defaults to config value)
            port: Port to bind to (defaults to config value)
            debug: Debug mode (defaults to config value)
            ssl_context: SSL context tuple (cert_file, key_file) or None
        """
        # Use provided values or fall back to config
        host = host or self.props.get('server.host', '0.0.0.0')
        port = port or self.props.get_int('server.port', 5001)
        debug = debug if debug is not None else self.props.get_bool('server.debug', True)

        # Run the application
        if ssl_context:
            self.app.run(host=host, port=port, debug=debug,
                        ssl_context=ssl_context, threaded=True)
        else:
            self.app.run(host=host, port=port, debug=debug, threaded=True)


# For backward compatibility - create a default instance
def create_app(config_file='application.properties'):
    """
    Application factory function

    Args:
        config_file: Path to the configuration file

    Returns:
        Tuple of (Flask app, PropertiesConfigurator)
    """
    abhikarta = AbhikartaApp(config_file)
    return abhikarta.get_app(), abhikarta.get_config()


# For direct execution (backward compatibility)
if __name__ == '__main__':
    abhikarta_app = AbhikartaApp()
    abhikarta_app.run()