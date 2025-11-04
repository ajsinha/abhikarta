"""
View Routes
Handles view-related pages including AI Insights

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import render_template, jsonify, request, send_file
from routes.base_routes import BaseRoutes
import os
import tempfile
import uuid
from pathlib import Path
from datetime import datetime


class ViewRoutes(BaseRoutes):
    """View routes handler"""

    def __init__(self, app, user_registry, login_required):
        super().__init__()
        self.app = app
        self.user_registry = user_registry
        self.login_required = login_required
        self.register_routes()

    def register_routes(self):
        """Register all view routes"""

        @self.app.route('/ai-insights')
        @self.login_required
        def ai_insights():
            """AI Insights page"""
            from flask import session
            user = self.user_registry.get_user(session.get('user_id'))

            return render_template(
                'ai_insights.html',
                user=user
            )

        @self.app.route('/api/insights')
        @self.login_required
        def api_get_insights():
            """API endpoint to fetch insights data from filesystem"""
            from flask import session

            user_id = session.get('user_id')

            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '').strip()
            sort_by = request.args.get('sort_by', 'document')
            sort_order = request.args.get('sort_order', 'asc')

            insights = []

            # Base directory for insights
            base_dir = 'data/ai_insights'

            # Load global insights from data/ai_insights/all
            global_dir = os.path.join(base_dir, 'all')
            if os.path.exists(global_dir):
                for filename in os.listdir(global_dir):
                    if filename.endswith('.md'):
                        filepath = os.path.join(global_dir, filename)
                        # Get file stats
                        try:
                            stat_info = os.stat(filepath)
                            created_at = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
                        except:
                            created_at = datetime.now().isoformat()

                        # Document name is filename without .md extension
                        document_name = filename[:-3] if filename.endswith('.md') else filename

                        insights.append({
                            'id': f"global_{filename}",
                            'category': 'Global',
                            'document': document_name,
                            'filepath': filepath,
                            'filename': filename,
                            'created_at': created_at
                        })

            # Load user-specific insights from data/ai_insights/users/<userid>
            user_dir = os.path.join(base_dir, 'users', user_id)
            if os.path.exists(user_dir):
                for filename in os.listdir(user_dir):
                    if filename.endswith('.md'):
                        filepath = os.path.join(user_dir, filename)
                        # Get file stats
                        try:
                            stat_info = os.stat(filepath)
                            created_at = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
                        except:
                            created_at = datetime.now().isoformat()

                        # Document name is filename without .md extension
                        document_name = filename[:-3] if filename.endswith('.md') else filename

                        insights.append({
                            'id': f"user_{filename}",
                            'category': 'User',
                            'document': document_name,
                            'filepath': filepath,
                            'filename': filename,
                            'created_at': created_at
                        })

            # Filter by search term
            if search:
                insights = [
                    item for item in insights
                    if search.lower() in item['category'].lower()
                    or search.lower() in item['document'].lower()
                ]

            # Sort data
            reverse = (sort_order == 'desc')
            insights.sort(key=lambda x: x.get(sort_by, ''), reverse=reverse)

            # Pagination
            total = len(insights)
            if per_page == -1:  # All items
                paginated_insights = insights
                total_pages = 1
            else:
                start = (page - 1) * per_page
                end = start + per_page
                paginated_insights = insights[start:end]
                total_pages = (total + per_page - 1) // per_page

            return jsonify({
                'success': True,
                'insights': paginated_insights,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            })

        @self.app.route('/api/insight/<insight_id>')
        @self.login_required
        def api_get_insight_content(insight_id):
            """API endpoint to fetch specific insight content from filesystem"""
            from flask import session

            user_id = session.get('user_id')

            # Parse insight_id (format: "global_filename.md" or "user_filename.md")
            if insight_id.startswith('global_'):
                filename = insight_id[7:]  # Remove "global_" prefix
                filepath = os.path.join('data/ai_insights/all', filename)
            elif insight_id.startswith('user_'):
                filename = insight_id[5:]  # Remove "user_" prefix
                filepath = os.path.join('data/ai_insights/users', user_id, filename)
            else:
                return jsonify({
                    'success': False,
                    'content': '# Error\n\nInvalid insight ID format.'
                }), 400

            # Read the markdown file
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    content = '# Insight Not Found\n\nThe requested insight could not be found.'
            except Exception as e:
                content = f'# Error Reading File\n\nCould not read the insight file: {str(e)}'

            return jsonify({
                'success': True,
                'content': content
            })

        @self.app.route('/api/export-insight/<insight_id>')
        @self.login_required
        def api_export_insight(insight_id):
            """API endpoint to export insight as Word document"""
            from flask import session

            user_id = session.get('user_id')

            # Parse insight_id and get filepath
            if insight_id.startswith('global_'):
                filename = insight_id[7:]  # Remove "global_" prefix
                filepath = os.path.join('data/ai_insights/all', filename)
            elif insight_id.startswith('user_'):
                filename = insight_id[5:]  # Remove "user_" prefix
                filepath = os.path.join('data/ai_insights/users', user_id, filename)
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid insight ID format'
                }), 400

            # Read the markdown content
            try:
                if not os.path.exists(filepath):
                    return jsonify({
                        'success': False,
                        'error': 'Insight not found'
                    }), 404

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Get document name from filename (without .md extension)
                document_name = filename[:-3] if filename.endswith('.md') else filename

            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Error reading file: {str(e)}'
                }), 500

            try:
                # Create temporary directory for processing
                temp_dir = tempfile.mkdtemp()

                # Generate safe filename from document name
                safe_filename = "".join(c for c in document_name if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_filename = safe_filename.replace(' ', '_')
                output_file = os.path.join(temp_dir, f'{safe_filename}.docx')

                # Convert markdown to docx using Python converter
                try:
                    # Import the converter (located in utils or static/js)
                    import sys
                    possible_paths = [
                        'utils',
                        'static/js',
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'utils'),
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'js'),
                    ]

                    converter_imported = False
                    for path in possible_paths:
                        if path not in sys.path:
                            sys.path.insert(0, path)
                        try:
                            from markdown_to_docx import convert_markdown_to_docx
                            converter_imported = True
                            print(f"✓ Imported converter from path containing: {path}")
                            break
                        except ImportError:
                            continue

                    if not converter_imported:
                        return jsonify({
                            'success': False,
                            'error': 'Markdown converter module not found. Please ensure markdown_to_docx.py is in utils/ or static/js/ directory.'
                        }), 500

                    # Convert the markdown to docx
                    convert_markdown_to_docx(content, output_file)
                    print(f"✓ Converted markdown to: {output_file}")

                except Exception as e:
                    print(f"Error during conversion: {e}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({
                        'success': False,
                        'error': f'Conversion failed: {str(e)}'
                    }), 500

                # Send the file
                return send_file(
                    output_file,
                    as_attachment=True,
                    download_name=f'{safe_filename}.docx',
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )

            except Exception as e:
                print(f"Error exporting insight: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
            finally:
                # Cleanup temp files (in production, use a background task)
                try:
                    import shutil
                    if os.path.exists(temp_dir):
                        shutil.rmtree(temp_dir)
                except:
                    pass

        @self.app.route('/api/delete-insight/<insight_id>', methods=['DELETE'])
        @self.login_required
        def api_delete_insight(insight_id):
            """API endpoint to delete a user insight"""
            from flask import session

            user_id = session.get('user_id')

            # Only allow deleting user insights, not global ones
            if not insight_id.startswith('user_'):
                return jsonify({
                    'success': False,
                    'error': 'Only user insights can be deleted'
                }), 403

            # Parse insight_id to get filename
            filename = insight_id[5:]  # Remove "user_" prefix
            filepath = os.path.join('data/ai_insights/users', user_id, filename)

            # Delete the file
            try:
                if not os.path.exists(filepath):
                    return jsonify({
                        'success': False,
                        'error': 'Insight not found'
                    }), 404

                os.remove(filepath)

                return jsonify({
                    'success': True,
                    'message': 'Insight deleted successfully'
                })

            except Exception as e:
                print(f"Error deleting insight: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Error deleting file: {str(e)}'
                }), 500