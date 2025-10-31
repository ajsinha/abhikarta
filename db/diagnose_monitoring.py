#!/usr/bin/env python3
"""
Diagnostic Script - Check why monitoring_users shows no data
Run this from your project root directory
"""

import sys
import json
from datetime import datetime, timedelta

print("=" * 70)
print("MONITORING USERS DIAGNOSTIC TOOL")
print("=" * 70)

# Step 1: Import the database handler
print("\n1. Testing imports...")
try:
    from db.database_call_handler import get_database_handler

    print("   ✓ DatabaseCallHandler imported")
except Exception as e:
    print(f"   ✗ Failed to import: {e}")
    sys.exit(1)

# Step 2: Get database instance
print("\n2. Getting database instance...")
try:
    db_handler = get_database_handler()
    print("   ✓ Database handler created")
except Exception as e:
    print(f"   ✗ Failed to create handler: {e}")
    sys.exit(1)

# Step 3: Check if tables exist
print("\n3. Checking if tables exist...")
tables_to_check = ['users', 'sessions', 'workflows', 'workflow_nodes']
table_status = {}
for table in tables_to_check:
    try:
        exists = db_handler.table_exists(table)
        table_status[table] = exists
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"   {status}: {table}")
    except Exception as e:
        print(f"   ✗ ERROR checking {table}: {e}")
        table_status[table] = False

# Step 4: Check users table
print("\n4. Checking users table...")
if table_status.get('users'):
    try:
        total_users = db_handler.count_total_users()
        print(f"   Total users in database: {total_users}")

        if total_users > 0:
            # Try to get some users
            users = db_handler.db.fetchall("SELECT user_id, username, role FROM users LIMIT 5")
            print(f"   Sample users:")
            for user in users:
                print(
                    f"     - {user.get('username', 'N/A')} (ID: {user.get('user_id', 'N/A')}, Role: {user.get('role', 'N/A')})")
        else:
            print("   ⚠ No users found in database!")
    except Exception as e:
        print(f"   ✗ Error reading users: {e}")
else:
    print("   ✗ Users table doesn't exist - can't check")

# Step 5: Check sessions table
print("\n5. Checking sessions table...")
if table_status.get('sessions'):
    try:
        # Count total sessions
        total_sessions = db_handler.db.fetchone("SELECT COUNT(*) as count FROM sessions")
        session_count = total_sessions['count'] if total_sessions else 0
        print(f"   Total sessions in database: {session_count}")

        if session_count > 0:
            # Get sample sessions
            sessions = db_handler.db.fetchall("""
                SELECT session_id, user_id, created_at, updated_at, status 
                FROM sessions 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            print(f"   Recent sessions:")
            for session in sessions:
                print(
                    f"     - User: {session.get('user_id', 'N/A')}, Status: {session.get('status', 'N/A')}, Created: {session.get('created_at', 'N/A')}")
        else:
            print("   ⚠ No sessions found in database!")
            print("   This is why the monitoring page shows no data.")
            print("   Sessions should be created when users login.")
    except Exception as e:
        print(f"   ✗ Error reading sessions: {e}")
else:
    print("   ✗ Sessions table doesn't exist!")
    print("   This is the problem - sessions table is required for monitoring.")

# Step 6: Check workflows
print("\n6. Checking workflows table...")
if table_status.get('workflows'):
    try:
        total_workflows = db_handler.db.fetchone("SELECT COUNT(*) as count FROM workflows")
        workflow_count = total_workflows['count'] if total_workflows else 0
        print(f"   Total workflows in database: {workflow_count}")

        if workflow_count > 0:
            # Get sample workflows
            workflows = db_handler.db.fetchall("""
                SELECT workflow_id, name, status, created_by, created_at 
                FROM workflows 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            print(f"   Recent workflows:")
            for wf in workflows:
                print(
                    f"     - {wf.get('name', 'N/A')} by {wf.get('created_by', 'N/A')}, Status: {wf.get('status', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Error reading workflows: {e}")
else:
    print("   ✗ Workflows table doesn't exist")

# Step 7: Test the actual monitoring methods
print("\n7. Testing monitoring methods...")
try:
    from monitoring.monitoring_service import MonitoringService

    monitoring = MonitoringService()
    print("   ✓ MonitoringService created")

    # Test get_user_stats
    print("\n   Testing get_user_stats()...")
    stats = monitoring.get_user_stats()

    print(f"   Results:")
    print(f"     - Today: {stats.get('today', 'N/A')}")
    print(f"     - Last 7 days: {stats.get('last_7_days', 'N/A')}")
    print(f"     - Total users: {stats.get('total', 'N/A')}")
    print(f"     - Hourly data points: {len(stats.get('hourly_data', []))}")
    print(f"     - Active sessions: {len(stats.get('active_sessions', []))}")
    print(f"     - User stats: {len(stats.get('user_stats', []))}")

    if stats.get('active_sessions'):
        print(f"\n   Active sessions found:")
        for session in stats['active_sessions'][:3]:
            print(f"     - {session}")

    if stats.get('user_stats'):
        print(f"\n   User statistics found:")
        for user in stats['user_stats'][:3]:
            print(f"     - {user}")

except Exception as e:
    print(f"   ✗ Error testing monitoring: {e}")
    import traceback

    traceback.print_exc()

# Step 8: Check database schema
print("\n8. Checking sessions table schema...")
if table_status.get('sessions'):
    try:
        schema = db_handler.db.fetchall("PRAGMA table_info(sessions)")
        print("   Sessions table columns:")
        for col in schema:
            print(f"     - {col['name']} ({col['type']})")
    except Exception as e:
        print(f"   ✗ Error checking schema: {e}")

# Step 9: Summary and recommendations
print("\n" + "=" * 70)
print("SUMMARY AND RECOMMENDATIONS")
print("=" * 70)

issues_found = []
recommendations = []

if not table_status.get('sessions'):
    issues_found.append("❌ CRITICAL: Sessions table doesn't exist")
    recommendations.append("Create sessions table with columns: session_id, user_id, created_at, updated_at, status")
elif table_status.get('sessions'):
    try:
        total_sessions = db_handler.db.fetchone("SELECT COUNT(*) as count FROM sessions")
        if total_sessions['count'] == 0:
            issues_found.append("⚠ WARNING: Sessions table is empty")
            recommendations.append("Ensure your login system creates session records in the database")
            recommendations.append("Check if session tracking is enabled in your Flask app")
    except:
        pass

if not table_status.get('users'):
    issues_found.append("❌ CRITICAL: Users table doesn't exist")
    recommendations.append("Create users table")
elif table_status.get('users'):
    try:
        if db_handler.count_total_users() == 0:
            issues_found.append("⚠ WARNING: Users table is empty")
            recommendations.append("Create at least one user account")
    except:
        pass

if issues_found:
    print("\nIssues Found:")
    for issue in issues_found:
        print(f"  {issue}")

    print("\nRecommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
else:
    print("\n✓ All checks passed - monitoring should be working")
    print("  If you still see empty cards, check:")
    print("  1. Browser console (F12) for JavaScript errors")
    print("  2. Network tab to see API response")
    print("  3. Try hard refresh (Ctrl+Shift+R)")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)