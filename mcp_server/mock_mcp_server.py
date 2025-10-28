"""
Mock MCP Server for Testing
Simulates MCP tool execution endpoints

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import Flask, request, jsonify
import random

app = Flask(__name__)


@app.route('/execute', methods=['POST'])
def execute():
    """Execute tool endpoint"""
    data = request.get_json()
    tool_name = data.get('tool')
    arguments = data.get('arguments', {})
    
    # Simulate tool execution
    if tool_name == 'echo':
        result = {
            'success': True,
            'output': f"Echo: {arguments.get('input', 'No input')}",
            'tool': tool_name
        }
    elif tool_name == 'get_stock_price':
        symbol = arguments.get('symbol', 'AAPL')
        result = {
            'success': True,
            'symbol': symbol,
            'price': round(random.uniform(100, 500), 2),
            'currency': 'USD',
            'tool': tool_name
        }
    elif tool_name == 'get_stock_info':
        symbol = arguments.get('symbol', 'AAPL')
        result = {
            'success': True,
            'symbol': symbol,
            'company_name': f'Company {symbol}',
            'market_cap': f'${random.randint(100, 3000)}B',
            'sector': 'Technology',
            'tool': tool_name
        }
    else:
        result = {
            'success': False,
            'error': f'Unknown tool: {tool_name}'
        }
    
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'server': 'Mock MCP Server'
    })


@app.route('/tools', methods=['GET'])
def list_tools():
    """List available tools"""
    return jsonify({
        'tools': [
            {
                'name': 'echo',
                'description': 'Echo back the input'
            },
            {
                'name': 'get_stock_price',
                'description': 'Get stock price for a symbol'
            },
            {
                'name': 'get_stock_info',
                'description': 'Get stock information'
            }
        ]
    })


if __name__ == '__main__':
    print("Starting Mock MCP Server on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
