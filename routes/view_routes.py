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
from datetime import datetime, timedelta
import time
import threading
import json
import base64


class ViewRoutes(BaseRoutes):
    """View routes handler"""

    def __init__(self, app, user_registry, login_required):
        super().__init__()
        self.app = app
        self.user_registry = user_registry
        self.login_required = login_required

        # Cleanup configuration
        # Get retention days from environment variable or use default
        self.retention_days = int(os.environ.get('AI_INSIGHTS_RETENTION_DAYS', '15'))
        self.cleanup_interval_hours = int(os.environ.get('AI_INSIGHTS_CLEANUP_INTERVAL_HOURS', '24'))

        print(f"AI Insights Cleanup Monitor Configuration:")
        print(f"  - Retention period: {self.retention_days} days")
        print(f"  - Cleanup interval: {self.cleanup_interval_hours} hours")

        self.register_routes()

        # Start the cleanup monitor in a background thread
        self._start_cleanup_monitor()

    def _cleanup_old_files(self):
        """
        Clean up markdown files older than retention_days from:
        - data/ai_insights/all/
        - data/ai_insights/users/*/
        """
        try:
            cutoff_time = time.time() - (self.retention_days * 24 * 60 * 60)
            deleted_count = 0
            base_dir = 'data/ai_insights'

            print(f"[Cleanup] Starting cleanup: Removing files older than {self.retention_days} days")
            print(f"[Cleanup] Cutoff date: {datetime.fromtimestamp(cutoff_time).strftime('%Y-%m-%d %H:%M:%S')}")

            # Clean up global insights (data/ai_insights/all)
            global_dir = os.path.join(base_dir, 'all')
            if os.path.exists(global_dir):
                deleted_count += self._cleanup_directory(global_dir, cutoff_time, 'Global')

            # Clean up user insights (data/ai_insights/users/*)
            users_dir = os.path.join(base_dir, 'users')
            if os.path.exists(users_dir):
                # Iterate through all user directories
                for user_folder in os.listdir(users_dir):
                    user_path = os.path.join(users_dir, user_folder)
                    if os.path.isdir(user_path):
                        deleted_count += self._cleanup_directory(user_path, cutoff_time, f'User:{user_folder}')

            if deleted_count > 0:
                print(f"[Cleanup] ✓ Completed: Deleted {deleted_count} old file(s)")
            else:
                print(f"[Cleanup] ✓ Completed: No old files to delete")

            return deleted_count

        except Exception as e:
            print(f"[Cleanup] ✗ Error during cleanup: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def _cleanup_directory(self, directory, cutoff_time, category):
        """
        Clean up old markdown files in a specific directory

        Args:
            directory (str): Directory path to clean
            cutoff_time (float): Unix timestamp cutoff
            category (str): Category name for logging

        Returns:
            int: Number of files deleted
        """
        deleted_count = 0

        try:
            if not os.path.exists(directory):
                return 0

            for filename in os.listdir(directory):
                if filename.endswith('.md'):
                    filepath = os.path.join(directory, filename)

                    try:
                        # Get file modification time
                        file_mtime = os.path.getmtime(filepath)

                        # Check if file is older than cutoff
                        if file_mtime < cutoff_time:
                            # Calculate age in days
                            age_days = (time.time() - file_mtime) / (24 * 60 * 60)
                            file_date = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d')

                            # Delete the file
                            os.remove(filepath)
                            deleted_count += 1
                            print(f"[Cleanup]   Deleted [{category}]: {filename} (created: {file_date}, age: {age_days:.1f} days)")

                    except Exception as e:
                        print(f"[Cleanup]   Error deleting {filepath}: {e}")

        except Exception as e:
            print(f"[Cleanup] Error accessing directory {directory}: {e}")

        return deleted_count

    def _start_cleanup_monitor(self):
        """Start background thread for periodic cleanup"""
        def cleanup_worker():
            # Run initial cleanup after a short delay
            time.sleep(60)  # Wait 1 minute before first cleanup

            while True:
                try:
                    self._cleanup_old_files()
                    # Sleep for the configured interval (converted to seconds)
                    time.sleep(self.cleanup_interval_hours * 3600)
                except Exception as e:
                    print(f"[Cleanup] Error in cleanup worker: {e}")
                    # Wait a bit before retrying
                    time.sleep(3600)  # Wait 1 hour on error

        # Start background thread
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True, name='AIInsightsCleanup')
        cleanup_thread.start()
        print(f"[Cleanup] ✓ Monitor started successfully")
        print(f"[Cleanup]   - Will run every {self.cleanup_interval_hours} hour(s)")
        print(f"[Cleanup]   - First cleanup in 1 minute, then every {self.cleanup_interval_hours} hour(s)")

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

                        # Create JSON-based ID
                        id_data = {
                            'category': 'Global',
                            'owner': 'admin',
                            'document': filename
                        }
                        # Encode as base64 for URL safety
                        id_json = json.dumps(id_data, separators=(',', ':'))
                        id_encoded = base64.urlsafe_b64encode(id_json.encode()).decode()

                        insights.append({
                            'id': id_encoded,
                            'category': 'Global',
                            'owner': 'admin',
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

                        # Create JSON-based ID
                        id_data = {
                            'category': 'User',
                            'owner': user_id,
                            'document': filename
                        }
                        # Encode as base64 for URL safety
                        id_json = json.dumps(id_data, separators=(',', ':'))
                        id_encoded = base64.urlsafe_b64encode(id_json.encode()).decode()

                        insights.append({
                            'id': id_encoded,
                            'category': 'User',
                            'owner': user_id,
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

        @self.app.route('/api/insight/<path:insight_id>')
        @self.login_required
        def api_get_insight_content(insight_id):
            """API endpoint to fetch specific insight content from filesystem"""
            from flask import session

            user_id = session.get('user_id')

            try:
                # Decode the JSON-based ID

                try:
                    id_json = base64.urlsafe_b64decode(insight_id.encode()).decode()
                    id_data = json.loads(id_json)

                    category = id_data.get('category')
                    owner = id_data.get('owner')
                    document = id_data.get('document')

                    if not all([category, owner, document]):
                        raise ValueError("Invalid ID structure")

                except Exception as e:
                    print(f"Error decoding insight ID: {e}")
                    return jsonify({
                        'success': False,
                        'content': '# Error\n\nInvalid insight ID format.'
                    }), 400

                # Determine file path based on category and owner
                base_dir = 'data/ai_insights'

                if category == 'Global':
                    filepath = os.path.join(base_dir, 'all', document)
                elif category == 'User':
                    # Verify user can only access their own insights
                    if owner != user_id:
                        return jsonify({
                            'success': False,
                            'content': '# Access Denied\n\nYou do not have permission to view this insight.'
                        }), 403
                    filepath = os.path.join(base_dir, 'users', owner, document)
                else:
                    return jsonify({
                        'success': False,
                        'content': '# Error\n\nInvalid category.'
                    }), 400

                # Read the file
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return jsonify({
                        'success': True,
                        'content': content,
                        'category': category,
                        'owner': owner,
                        'document': document
                    })
                else:
                    return jsonify({
                        'success': False,
                        'content': '# Insight Not Found\n\nThe requested insight could not be found.'
                    }), 404

            except Exception as e:
                print(f"Error loading insight content: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'content': f'# Error\n\nFailed to load insight: {str(e)}'
                }), 500

        @self.app.route('/api/export-insight/<path:insight_id>')
        @self.login_required
        def api_export_insight(insight_id):
            """API endpoint to export insight as Word document"""
            from flask import session

            user_id = session.get('user_id')

            try:
                # Decode the JSON-based ID

                try:
                    id_json = base64.urlsafe_b64decode(insight_id.encode()).decode()
                    id_data = json.loads(id_json)

                    category = id_data.get('category')
                    owner = id_data.get('owner')
                    document = id_data.get('document')

                    if not all([category, owner, document]):
                        raise ValueError("Invalid ID structure")

                except Exception as e:
                    print(f"Error decoding insight ID: {e}")
                    return jsonify({
                        'success': False,
                        'error': 'Invalid insight ID format'
                    }), 400

                # Determine file path based on category and owner
                base_dir = 'data/ai_insights'

                if category == 'Global':
                    filepath = os.path.join(base_dir, 'all', document)
                elif category == 'User':
                    # Verify user can only export their own insights
                    if owner != user_id:
                        return jsonify({
                            'success': False,
                            'error': 'Access denied: You can only export your own insights'
                        }), 403
                    filepath = os.path.join(base_dir, 'users', owner, document)
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid category'
                    }), 400

                # Read the markdown content
                if not os.path.exists(filepath):
                    return jsonify({
                        'success': False,
                        'error': 'Insight not found'
                    }), 404

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Get document name from filename (without .md extension)
                document_name = document[:-3] if document.endswith('.md') else document

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

        @self.app.route('/api/delete-insight/<path:insight_id>', methods=['DELETE'])
        @self.login_required
        def api_delete_insight(insight_id):
            """API endpoint to delete a user insight"""
            from flask import session

            user_id = session.get('user_id')

            try:
                # Decode the JSON-based ID

                try:
                    id_json = base64.urlsafe_b64decode(insight_id.encode()).decode()
                    id_data = json.loads(id_json)

                    category = id_data.get('category')
                    owner = id_data.get('owner')
                    document = id_data.get('document')

                    if not all([category, owner, document]):
                        raise ValueError("Invalid ID structure")

                except Exception as e:
                    print(f"Error decoding insight ID: {e}")
                    return jsonify({
                        'success': False,
                        'error': 'Invalid insight ID format'
                    }), 400

                # Only allow deleting user insights, not global ones
                if category != 'User':
                    return jsonify({
                        'success': False,
                        'error': 'Only user insights can be deleted'
                    }), 403

                # Verify user can only delete their own insights
                if owner != user_id:
                    return jsonify({
                        'success': False,
                        'error': 'Access denied: You can only delete your own insights'
                    }), 403

                # Build filepath
                filepath = os.path.join('data/ai_insights/users', owner, document)

                # Delete the file
                if not os.path.exists(filepath):
                    return jsonify({
                        'success': False,
                        'error': 'Insight not found'
                    }), 404

                os.remove(filepath)
                print(f"Deleted insight: {filepath}")

                return jsonify({
                    'success': True,
                    'message': 'Insight deleted successfully'
                })

            except Exception as e:
                print(f"Error deleting insight: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'error': f'Error deleting file: {str(e)}'
                }), 500

        @self.app.route('/api/cleanup-insights', methods=['POST'])
        @self.login_required
        def api_manual_cleanup():
            """API endpoint to manually trigger cleanup of old insights"""
            from flask import session

            # Check if user is admin (optional - remove if you want all users to trigger cleanup)
            user = self.user_registry.get_user(session.get('user_id'))
            if not user or not hasattr(user, 'is_admin') or not user.is_admin():
                return jsonify({
                    'success': False,
                    'error': 'Admin access required'
                }), 403

            try:
                deleted_count = self._cleanup_old_insights()
                return jsonify({
                    'success': True,
                    'message': f'Cleanup completed: {deleted_count} file(s) deleted',
                    'deleted_count': deleted_count,
                    'retention_days': self.retention_days
                })
            except Exception as e:
                print(f"Error during manual cleanup: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        @self.app.route('/api/cleanup-status')
        @self.login_required
        def api_cleanup_status():
            """API endpoint to get cleanup configuration and statistics"""
            from flask import session

            user = self.user_registry.get_user(session.get('user_id'))

            try:
                # Count total files
                base_dir = 'data/ai_insights'
                total_files = 0
                old_files = 0
                cutoff_time = datetime.now() - timedelta(days=self.retention_days)

                # Count files in global directory
                global_dir = os.path.join(base_dir, 'all')
                if os.path.exists(global_dir):
                    for filename in os.listdir(global_dir):
                        if filename.endswith('.md'):
                            total_files += 1
                            filepath = os.path.join(global_dir, filename)
                            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                            if file_mtime < cutoff_time:
                                old_files += 1

                # Count files in user directories
                users_dir = os.path.join(base_dir, 'users')
                if os.path.exists(users_dir):
                    for user_folder in os.listdir(users_dir):
                        user_path = os.path.join(users_dir, user_folder)
                        if os.path.isdir(user_path):
                            for filename in os.listdir(user_path):
                                if filename.endswith('.md'):
                                    total_files += 1
                                    filepath = os.path.join(user_path, filename)
                                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                                    if file_mtime < cutoff_time:
                                        old_files += 1

                return jsonify({
                    'success': True,
                    'retention_days': self.retention_days,
                    'cleanup_interval_hours': self.cleanup_interval_hours,
                    'total_insights': total_files,
                    'old_insights': old_files,
                    'cutoff_date': cutoff_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'can_trigger_cleanup': user and hasattr(user, 'is_admin') and user.is_admin()
                })
            except Exception as e:
                print(f"Error getting cleanup status: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

    def _start_cleanup_monitor(self):
        """Start the background cleanup monitor thread"""
        def cleanup_worker():
            while True:
                try:
                    # Wait for the configured interval before first cleanup
                    time.sleep(self.cleanup_interval_hours * 3600)

                    # Run cleanup
                    self._cleanup_old_insights()

                except Exception as e:
                    print(f"Error in cleanup monitor: {e}")
                    import traceback
                    traceback.print_exc()

        # Create and start daemon thread
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        print(f"✓ AI Insights cleanup monitor started (runs every {self.cleanup_interval_hours} hours)")

    def _cleanup_old_insights(self):
        """
        Clean up old markdown files from insights directories
        Deletes files older than self.retention_days
        """
        print("\n" + "=" * 60)
        print(f"AI Insights Cleanup: Starting cleanup process")
        print(f"Retention period: {self.retention_days} days")
        print("=" * 60)

        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0

        # Base directory for insights
        base_dir = 'data/ai_insights'

        # Clean up global insights from data/ai_insights/all
        global_dir = os.path.join(base_dir, 'all')
        if os.path.exists(global_dir):
            print(f"\nScanning: {global_dir}")
            count = self._cleanup_directory(global_dir, cutoff_time)
            deleted_count += count
            print(f"  → Deleted {count} file(s) from global directory")

        # Clean up user insights from all subdirectories of data/ai_insights/users
        users_dir = os.path.join(base_dir, 'users')
        if os.path.exists(users_dir):
            print(f"\nScanning: {users_dir}")

            # Iterate through all user directories
            try:
                for user_folder in os.listdir(users_dir):
                    user_path = os.path.join(users_dir, user_folder)

                    # Only process directories
                    if os.path.isdir(user_path):
                        print(f"  Checking user folder: {user_folder}")
                        count = self._cleanup_directory(user_path, cutoff_time)
                        deleted_count += count
                        if count > 0:
                            print(f"    → Deleted {count} file(s)")
            except Exception as e:
                print(f"  Error scanning users directory: {e}")

        print("\n" + "=" * 60)
        print(f"Cleanup completed: {deleted_count} total file(s) deleted")
        print("=" * 60 + "\n")

        return deleted_count

    def _cleanup_directory(self, directory, cutoff_time):
        """
        Clean up old .md files from a specific directory

        Args:
            directory (str): Path to directory to clean
            cutoff_time (datetime): Delete files older than this time

        Returns:
            int: Number of files deleted
        """
        deleted_count = 0

        try:
            for filename in os.listdir(directory):
                # Only process .md files
                if not filename.endswith('.md'):
                    continue

                filepath = os.path.join(directory, filename)

                # Only process files, not directories
                if not os.path.isfile(filepath):
                    continue

                try:
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

                    # Check if file is older than cutoff time
                    if file_mtime < cutoff_time:
                        # Delete the file
                        os.remove(filepath)
                        deleted_count += 1

                        age_days = (datetime.now() - file_mtime).days
                        print(f"    ✓ Deleted: {filename} (age: {age_days} days)")

                except Exception as e:
                    print(f"    ✗ Error processing {filename}: {e}")

        except Exception as e:
            print(f"  Error accessing directory {directory}: {e}")

        return deleted_count