"""
Authentication Routes
Handles user login and logout

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import request, redirect, url_for, session, render_template, flash
from functools import wraps
from datetime import datetime


class AuthRoutes:
    """Authentication routes handler"""
    
    def __init__(self, app, user_registry, get_db):
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
                    session['user_id'] = user.user_id
                    session['username'] = user.username
                    session['role'] = user.role
                    
                    # Update last login
                    db = self.get_db()
                    db.execute(
                        "INSERT OR REPLACE INTO users (user_id, username, full_name, email, role, last_login) VALUES (?, ?, ?, ?, ?, ?)",
                        (user.user_id, user.username, user.full_name, user.email, user.role, datetime.now().isoformat())
                    )
                    
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """Logout"""
            session.clear()
            flash('Logged out successfully', 'info')
            return redirect(url_for('login'))
