#!/usr/bin/env python3
"""
Automatic Patcher for database_call_handler.py
This script will automatically fix your database_call_handler.py file

BACKUP: This script creates a backup before making changes
"""

import os
import sys
from datetime import datetime


def backup_file(filepath):
    """Create a timestamped backup of the file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"✓ Created backup: {backup_path}")
        return True
    else:
        print(f"✗ File not found: {filepath}")
        return False


def read_file(filepath):
    """Read the file content"""
    with open(filepath, 'r') as f:
        return f.read()


def write_file(filepath, content):
    """Write content to file"""
    with open(filepath, 'w') as f:
        f.write(content)


def patch_database_handler(filepath):
    """Apply the patch to database_call_handler.py"""

    print("\n" + "=" * 60)
    print("DATABASE CALL HANDLER PATCHER")
    print("=" * 60)

    # Create backup
    print("\n1. Creating backup...")
    if not backup_file(filepath):
        return False

    # Read file
    print("\n2. Reading file...")
    content = read_file(filepath)

    # Check if already patched
    if 'def count_distinct_users_in_sessions(self' in content:
        print("\n⚠️  File appears to already be patched!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborting.")
            return False

    # Find insertion point (before table_exists)
    print("\n3. Finding insertion point...")
    marker = "    # Utility Methods\n    def table_exists(self, table_name: str) -> bool:"

    if marker not in content:
        # Try alternative marker
        marker = "    def table_exists(self, table_name: str) -> bool:"
        if marker not in content:
            print("✗ Could not find insertion point (table_exists method)")
            print("Please patch manually using STEP_BY_STEP_FIX.md")
            return False

    print("✓ Found insertion point")

    # New methods to insert
    new_methods = '''
    # ==================== USER MONITORING METHODS ====================

    def count_distinct_users_in_sessions(self, since_time: str) -> int:
        """Count distinct users who have had sessions since a given time"""
        try:
            if not self.table_exists('sessions'):
                return 0
            result = self.db.fetchone("""
                SELECT COUNT(DISTINCT user_id) as count 
                FROM sessions 
                WHERE created_at >= ? OR updated_at >= ?
            """, (since_time, since_time))
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting distinct users in sessions: {e}")
            return 0

    def count_total_users(self) -> int:
        """Count total number of users in the system"""
        try:
            if not self.table_exists('users'):
                return 0
            result = self.db.fetchone("SELECT COUNT(*) as count FROM users")
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting total users: {e}")
            return 0

    def count_sessions_in_time_range(self, start_time: str, end_time: str) -> int:
        """Count sessions created within a time range"""
        try:
            if not self.table_exists('sessions'):
                return 0
            result = self.db.fetchone("""
                SELECT COUNT(*) as count 
                FROM sessions 
                WHERE created_at >= ? AND created_at < ?
            """, (start_time, end_time))
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting sessions in time range: {e}")
            return 0

    def get_active_sessions_with_users(self, limit: int = 10) -> list:
        """Get active sessions with user information"""
        try:
            if not self.table_exists('sessions') or not self.table_exists('users'):
                return []
            results = self.db.fetchall("""
                SELECT 
                    s.session_id,
                    s.user_id,
                    s.created_at,
                    s.updated_at,
                    s.status,
                    u.username
                FROM sessions s
                LEFT JOIN users u ON s.user_id = u.user_id
                WHERE s.status = 'active'
                ORDER BY s.updated_at DESC
                LIMIT ?
            """, (limit,))
            return results if results else []
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            return []

    def get_user_statistics(self, limit: int = 10) -> list:
        """Get user statistics including session counts and workflow counts"""
        try:
            if not self.table_exists('users'):
                return []
            has_sessions = self.table_exists('sessions')
            has_workflows = self.table_exists('workflows')

            if has_sessions and has_workflows:
                query = """
                    SELECT 
                        u.user_id,
                        u.username,
                        u.role,
                        (SELECT MAX(created_at) FROM sessions WHERE user_id = u.user_id) as last_login,
                        (SELECT COUNT(*) FROM sessions WHERE user_id = u.user_id) as session_count,
                        (SELECT COUNT(*) FROM workflows WHERE created_by = u.user_id) as workflow_count
                    FROM users u
                    ORDER BY last_login DESC
                    LIMIT ?
                """
            elif has_sessions:
                query = """
                    SELECT 
                        u.user_id,
                        u.username,
                        u.role,
                        (SELECT MAX(created_at) FROM sessions WHERE user_id = u.user_id) as last_login,
                        (SELECT COUNT(*) FROM sessions WHERE user_id = u.user_id) as session_count,
                        0 as workflow_count
                    FROM users u
                    ORDER BY last_login DESC
                    LIMIT ?
                """
            else:
                query = """
                    SELECT 
                        u.user_id,
                        u.username,
                        u.role,
                        NULL as last_login,
                        0 as session_count,
                        0 as workflow_count
                    FROM users u
                    ORDER BY u.username
                    LIMIT ?
                """

            results = self.db.fetchall(query, (limit,))
            return results if results else []
        except Exception as e:
            print(f"Error getting user statistics: {e}")
            return []

    def get_user_login_activity(self, user_id: str, limit: int = 10) -> list:
        """Get login activity for a specific user"""
        try:
            if not self.table_exists('sessions'):
                return []
            results = self.db.fetchall("""
                SELECT 
                    session_id,
                    user_id,
                    created_at as login_time,
                    updated_at as last_activity,
                    status
                FROM sessions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            return results if results else []
        except Exception as e:
            print(f"Error getting user login activity: {e}")
            return []

    # Utility Methods
'''

    # Insert new methods
    print("\n4. Inserting new methods...")
    content = content.replace(marker, new_methods + "    def table_exists(self, table_name: str) -> bool:")

    # Fix broken helper methods if they exist
    print("\n5. Checking for broken helper methods...")
    if 'def count_where(self, table_name, where_clause, params):\n    """Generic count with where clause"""\n    query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause}"\n    result = self.execute_query(query, params)' in content:
        print("   Found broken count_where - fixing...")
        content = content.replace(
            'def count_where(self, table_name, where_clause, params):\n    """Generic count with where clause"""\n    query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause}"\n    result = self.execute_query(query, params)',
            'def count_where(self, table_name, where_clause, params):\n    """Generic count with where clause - FIXED"""\n    try:\n        query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause}"\n        result = self.db.fetchone(query, params)\n        return result.get(\'count\', 0) if result else 0\n    except Exception as e:\n        print(f"Error in count_where: {e}")\n        return 0\n\ndef _old_count_where(self, table_name, where_clause, params):\n    """OLD BROKEN VERSION - DO NOT USE"""\n    query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause}"\n    result = None  # self.execute_query(query, params)'
        )

    if 'def count_all(self, table_name):\n    """Generic count all rows in a table"""\n    query = f"SELECT COUNT(*) as count FROM {table_name}"\n    result = self.execute_query(query)' in content:
        print("   Found broken count_all - fixing...")
        content = content.replace(
            'def count_all(self, table_name):\n    """Generic count all rows in a table"""\n    query = f"SELECT COUNT(*) as count FROM {table_name}"\n    result = self.execute_query(query)',
            'def count_all(self, table_name):\n    """Generic count all rows in a table - FIXED"""\n    try:\n        query = f"SELECT COUNT(*) as count FROM {table_name}"\n        result = self.db.fetchone(query)\n        return result.get(\'count\', 0) if result else 0\n    except Exception as e:\n        print(f"Error in count_all: {e}")\n        return 0\n\ndef _old_count_all(self, table_name):\n    """OLD BROKEN VERSION - DO NOT USE"""\n    query = f"SELECT COUNT(*) as count FROM {table_name}"\n    result = None  # self.execute_query(query)'
        )

    # Write patched file
    print("\n6. Writing patched file...")
    write_file(filepath, content)

    print("\n" + "=" * 60)
    print("✓ PATCHING COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart your Flask application")
    print("2. Navigate to /monitoring/users")
    print("3. The page should now show data")
    print("\nIf issues persist, check Flask console for errors")
    print("=" * 60)

    return True


if __name__ == '__main__':
    # Determine file path
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Try common locations
        possible_paths = [
            'db/database_call_handler.py',
            'database_call_handler.py',
            '../db/database_call_handler.py',
        ]

        filepath = None
        for path in possible_paths:
            if os.path.exists(path):
                filepath = path
                break

        if not filepath:
            print("Error: Could not find database_call_handler.py")
            print("\nUsage:")
            print("  python patch_database_handler.py [path/to/database_call_handler.py]")
            print("\nOr run from your project root directory")
            sys.exit(1)

    print(f"Target file: {filepath}")

    if patch_database_handler(filepath):
        sys.exit(0)
    else:
        sys.exit(1)