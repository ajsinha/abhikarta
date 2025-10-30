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

# Import and run the Flask app
from web.app import app, props

if __name__ == '__main__':
    print("=" * 60)
    print("Abhikarta - Multi-Agent Orchestration System")
    print("© 2025-2030 Ashutosh Sinha")
    print("ajsinha@gmail.com")
    print("https://www.github.com/ajsinha/abhikarta")
    print("=" * 60)
    
    host = props.get('server.host', '0.0.0.0')
    port = props.get_int('server.port', 5001)
    debug = props.get_bool('server.debug', True)
    
    print(f"\nStarting server on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print("\nDefault login: admin / admin")
    print("\nMake sure to start the Mock MCP Server on port 8000:")
    print("  python3 mcp_server/mock_mcp_server.py")
    print("=" * 60)
    print()

    cert_file = props.get('server.cert.file', None)
    key_file = props.get('server.key.file', None)
    # Run Flask app
    if not cert_file and not key_file:
        app.run(host=host, port=port, debug=debug)
    else:
        app.run(host=host, port=port, debug=debug, ssl_context=(cert_file, key_file))
