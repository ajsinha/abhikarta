"""
Authentication Routes
Handles user login and logout

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import request, redirect, url_for, session, render_template, flash
from functools import wraps
from datetime import datetime
import uuid
from routes.base_routes import BaseRoutes

class AuthRoutes(BaseRoutes):
    """Authentication routes handler"""

    def __init__(self, app, user_registry, get_db):
        super().__init__()

        self.app = app
        self.user_registry = user_registry
        self.get_db = get_db
        self.register_routes()

    def get_user(self, user_id):
        """Get user from database - simplified for demo"""
        # In production, fetch from database
        return self.user_registry.get_user(user_id)

    def login_required(self, f):
        """Authentication decorator"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def admin_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            # Simplified admin check - in production, check user role from database
            user = self.get_user(session['user_id'])
            if not user or not user.get('is_admin'):
                flash('Admin access required', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)

        return decorated_function

    def register_routes(self):
        """Register all authentication routes"""

        @self.app.route('/')
        def index():
            """Home page"""
            if 'user_id' in session:
                return redirect(url_for('dashboard'))
            return redirect(url_for('login'))

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Login page"""
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                user = self.user_registry.authenticate(username, password)
                if user:
                    # Set Flask session variables
                    session['user_id'] = user.user_id
                    session['username'] = user.username
                    session['role'] = user.role

                    db = self.get_db()
                    now = datetime.now().isoformat()

                    # Update last login in users table
                    db.execute(
                        "INSERT OR REPLACE INTO users (user_id, username, full_name, email, role, last_login) VALUES (?, ?, ?, ?, ?, ?)",
                        (user.user_id, user.username, user.full_name, user.email, user.role, now)
                    )

                    # ==================== FIX: CREATE SESSION RECORD ====================
                    # Create a session record in the database for monitoring
                    session_id = str(uuid.uuid4())
                    session['session_id'] = session_id  # Store in Flask session too

                    # Check if sessions table exists, create if not
                    try:
                        db.execute("""
                            CREATE TABLE IF NOT EXISTS sessions (
                                session_id TEXT PRIMARY KEY,
                                user_id TEXT NOT NULL,
                                created_at TEXT NOT NULL,
                                updated_at TEXT NOT NULL,
                                status TEXT DEFAULT 'active'
                            )
                        """)
                    except:
                        pass  # Table might already exist

                    # Insert session record
                    try:
                        db.execute("""
                            INSERT INTO sessions (session_id, user_id, created_at, updated_at, status)
                            VALUES (?, ?, ?, ?, 'active')
                        """, (session_id, user.user_id, now, now))

                        print(f"✓ Created session record: {session_id[:8]}... for user {user.username}")
                    except Exception as e:
                        print(f"Warning: Could not create session record: {e}")
                        # Don't fail login if session tracking fails
                    # ====================================================================

                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')

            return render_template('login.html')

        @self.app.route('/logout')
        def logout():
            """Logout"""
            # ==================== FIX: UPDATE SESSION STATUS ====================
            # Mark session as inactive when user logs out
            if 'session_id' in session and 'user_id' in session:
                try:
                    db = self.get_db()
                    now = datetime.now().isoformat()
                    db.execute("""
                        UPDATE sessions 
                        SET status = 'inactive', updated_at = ?
                        WHERE session_id = ?
                    """, (now, session['session_id']))
                    print(f"✓ Session {session['session_id'][:8]}... marked inactive")
                except Exception as e:
                    print(f"Warning: Could not update session: {e}")
            # ====================================================================

            session.clear()
            flash('Logged out successfully', 'info')
            return redirect(url_for('login'))


        @self.app.route('/admin/diagnose')
        def diagnose():
            from db.database_call_handler import get_database_handler

            db = get_database_handler()

            # Check tables
            print("\n=== TABLES ===")
            for table in ['plans', 'lgraph_plans', 'workflow_executions', 'sessions', 'users']:
                exists = db.table_exists(table)
                print(f"{table}: {'EXISTS' if exists else 'MISSING'}")

                if exists:
                    try:
                        # Use the db.db directly since execute_query doesn't exist
                        count_result = db.db.fetchone(f"SELECT COUNT(*) as count FROM {table}")
                        count = count_result['count'] if count_result else 0
                        print(f"  → {count} records")

                        # Show recent
                        recent = db.db.fetchall(f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT 1")
                        if recent:
                            print(f"  → Latest: {recent[0]}")
                    except Exception as e:
                        print(f"  → Error: {e}")

            return "Check console output"