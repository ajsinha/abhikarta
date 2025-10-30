#!/usr/bin/env python3
"""
Abhikarta Server Startup Script
Main entry point for the application

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the AbhikartaApp class
from web.app import AbhikartaApp


def print_banner(abhikarta_app):
    """Print startup banner with configuration details"""
    props = abhikarta_app.get_config()

    host = props.get('server.host', '0.0.0.0')
    port = props.get_int('server.port', 5001)
    debug = props.get_bool('server.debug', True)

    print("=" * 60)
    print("Abhikarta - Multi-Agent Orchestration System")
    print("© 2025-2030 Ashutosh Sinha")
    print("ajsinha@gmail.com")
    print("https://www.github.com/ajsinha/abhikarta")
    print("=" * 60)
    print(f"\nStarting server on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print("\nDefault login: admin / admin")
    print("\nMake sure to start the Mock MCP Server on port 8000:")
    print("  python3 mcp_server/mock_mcp_server.py")
    print("=" * 60)
    print()


def main():
    """Main entry point"""
    try:
        # Initialize the Abhikarta application
        abhikarta_app = AbhikartaApp(config_file='application.properties')

        # Print startup banner
        print_banner(abhikarta_app)

        # Get configuration
        props = abhikarta_app.get_config()

        # Get server configuration
        host = props.get('server.host', '0.0.0.0')
        port = props.get_int('server.port', 5001)
        debug = props.get_bool('server.debug', True)

        # Check for SSL configuration
        cert_file = props.get('server.cert.file', None)
        key_file = props.get('server.key.file', None)

        # Prepare SSL context if certificates are configured
        ssl_context = None
        if cert_file and key_file:
            ssl_context = (cert_file, key_file)
            print(f"SSL enabled with cert: {cert_file}")
            print()

        # Run the application
        abhikarta_app.run(
            host=host,
            port=port,
            debug=debug,
            ssl_context=ssl_context
        )

    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()