"""
Tool Routes
Tool management, execution, and administration

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import session, render_template, request, redirect, url_for, flash, jsonify


class ToolRoutes:
    """Tool routes handler"""
    
    def __init__(self, app, user_registry, tool_registry, login_required):
        self.app = app
        self.user_registry = user_registry
        self.tool_registry = tool_registry
        self.login_required = login_required
        self.register_routes()
    
    def register_routes(self):
        """Register all tool routes"""
        
        # ============== TOOL LISTING ==============
        
        @self.app.route('/tools')
        @self.login_required
        def tools():
            """Tools management page"""
            user = self.user_registry.get_user(session['user_id'])
            all_tools = self.tool_registry.list_tools()

            # Filter tools based on user access
            if not user.is_admin():
                all_tools = [t for t in all_tools if user.has_tool_access(t['tool_name'])]

            return render_template('tools.html', user=user, tools=all_tools)
        
        # ============== TOOL EXECUTION ==============
        
        @self.app.route('/execute_tool')
        @self.login_required
        def execute_tool_page():
            """Tool execution page"""
            user = self.user_registry.get_user(session['user_id'])
            all_tools = self.tool_registry.list_tools()

            # Filter tools based on user access
            if not user.is_admin():
                all_tools = [t for t in all_tools if user.has_tool_access(t['tool_name'])]

            return render_template('execute_tool.html', user=user, tools=all_tools)
        
        @self.app.route('/execute_tool/<tool_name>')
        @self.login_required
        def execute_tool_form(tool_name):
            """Tool execution form"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.has_tool_access(tool_name):
                flash('Access denied to this tool', 'danger')
                return redirect(url_for('execute_tool_page'))

            tool_info = self.tool_registry.get_tool_info(tool_name)
            if not tool_info:
                flash('Tool not found', 'danger')
                return redirect(url_for('execute_tool_page'))

            return render_template('execute_tool_form.html', user=user, tool=tool_info)
        
        @self.app.route('/api/execute_tool', methods=['POST'])
        @self.login_required
        def api_execute_tool():
            """API endpoint to execute a tool"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()
            tool_name = data.get('tool_name')
            params = data.get('params', {})

            if not user.has_tool_access(tool_name):
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            result = self.tool_registry.execute_tool(tool_name, **params)

            return jsonify(result)
        
        # ============== TOOL MANAGEMENT (ADMIN) ==============
        
        @self.app.route('/create_tool')
        @self.login_required
        def create_tool_page():
            """Create tool page (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                flash('Access denied. Admin only.', 'danger')
                return redirect(url_for('tools'))

            return render_template('create_tool.html', user=user)
        
        @self.app.route('/api/create_tool', methods=['POST'])
        @self.login_required
        def api_create_tool():
            """API endpoint to create a new tool (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied. Admin only.'}), 403

            data = request.get_json()
            result = self.tool_registry.create_tool_from_json(data)

            return jsonify(result)
        
        @self.app.route('/api/tool/enable/<tool_name>', methods=['POST'])
        @self.login_required
        def api_enable_tool(tool_name):
            """API endpoint to enable a tool (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            if self.tool_registry.enable_tool(tool_name):
                return jsonify({'success': True, 'message': f'Tool {tool_name} enabled'})
            else:
                return jsonify({'success': False, 'error': 'Failed to enable tool'}), 400
        
        @self.app.route('/api/tool/disable/<tool_name>', methods=['POST'])
        @self.login_required
        def api_disable_tool(tool_name):
            """API endpoint to disable a tool (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            if self.tool_registry.disable_tool(tool_name):
                return jsonify({'success': True, 'message': f'Tool {tool_name} disabled'})
            else:
                return jsonify({'success': False, 'error': 'Failed to disable tool'}), 400
        
        @self.app.route('/api/toggle_tool', methods=['POST'])
        @self.login_required
        def api_toggle_tool():
            """API endpoint to toggle tool enable/disable (admin only)"""
            user = self.user_registry.get_user(session['user_id'])

            if not user.is_admin():
                return jsonify({'success': False, 'error': 'Access denied'}), 403

            data = request.get_json()
            tool_name = data.get('tool_name')
            action = data.get('action')  # 'enable' or 'disable'

            if action == 'enable':
                result = self.tool_registry.enable_tool(tool_name)
                if result:
                    return jsonify({'success': True, 'message': f'Tool {tool_name} enabled'})
                else:
                    return jsonify({'success': False, 'error': f'Failed to enable tool {tool_name}'}), 400
            elif action == 'disable':
                result = self.tool_registry.disable_tool(tool_name)
                if result:
                    return jsonify({'success': True, 'message': f'Tool {tool_name} disabled'})
                else:
                    return jsonify({'success': False, 'error': f'Failed to disable tool {tool_name}'}), 400
            else:
                return jsonify({'success': False, 'error': 'Invalid action. Must be "enable" or "disable"'}), 400

            return jsonify({'success': False, 'error': 'Failed to toggle tool'}), 400