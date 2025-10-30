"""
DIAGNOSTIC SCRIPT - Run this to find the problem
Add this to your Flask app or run as standalone

© 2025-2030 Ashutosh Sinha
"""


def diagnose_monitoring_issue(db_handler):
    """Diagnose why plans aren't showing in monitoring"""

    print("\n" + "=" * 60)
    print("DIAGNOSTIC REPORT - Monitoring Issues")
    print("=" * 60)

    # 1. Check if tables exist
    print("\n1. CHECKING TABLES...")
    tables_to_check = [
        'plans',
        'lgraph_plans',
        'workflow_executions',
        'planner_conversations',
        'lgraph_conversations',
        'users',
        'dags'
    ]

    existing_tables = []
    missing_tables = []

    for table in tables_to_check:
        exists = db_handler.table_exists(table)
        if exists:
            existing_tables.append(table)
            print(f"   ✅ {table} - EXISTS")
        else:
            missing_tables.append(table)
            print(f"   ❌ {table} - MISSING")

    # 2. Count records in each table
    print("\n2. COUNTING RECORDS...")
    for table in existing_tables:
        try:
            count = db_handler.count_all(table)
            print(f"   {table}: {count} records")
        except Exception as e:
            print(f"   {table}: ERROR - {e}")

    # 3. Check recent plans
    print("\n3. CHECKING RECENT PLANS...")

    if 'plans' in existing_tables:
        try:
            query = "SELECT plan_id, user_id, status, created_at FROM plans ORDER BY created_at DESC LIMIT 3"
            results = db_handler.execute_query(query)
            if results:
                print(f"   Regular Plans: {len(results)} found")
                for plan in results:
                    print(
                        f"      - {plan.get('plan_id', 'N/A')[:12]}... | {plan.get('status')} | {plan.get('created_at')}")
            else:
                print("   Regular Plans: EMPTY TABLE")
        except Exception as e:
            print(f"   Regular Plans: ERROR - {e}")

    if 'lgraph_plans' in existing_tables:
        try:
            query = "SELECT plan_id, user_id, status, created_at FROM lgraph_plans ORDER BY created_at DESC LIMIT 3"
            results = db_handler.execute_query(query)
            if results:
                print(f"   LangGraph Plans: {len(results)} found")
                for plan in results:
                    print(
                        f"      - {plan.get('plan_id', 'N/A')[:12]}... | {plan.get('status')} | {plan.get('created_at')}")
            else:
                print("   LangGraph Plans: EMPTY TABLE")
        except Exception as e:
            print(f"   LangGraph Plans: ERROR - {e}")

    # 4. Check workflow executions
    print("\n4. CHECKING WORKFLOW EXECUTIONS...")

    if 'workflow_executions' in existing_tables:
        try:
            query = "SELECT execution_id, dag_id, status, start_time FROM workflow_executions ORDER BY start_time DESC LIMIT 3"
            results = db_handler.execute_query(query)
            if results:
                print(f"   Executions: {len(results)} found")
                for exec in results:
                    print(
                        f"      - {exec.get('execution_id', 'N/A')[:12]}... | {exec.get('status')} | {exec.get('start_time')}")
            else:
                print("   Executions: EMPTY TABLE")
        except Exception as e:
            print(f"   Executions: ERROR - {e}")

    # 5. Check table schemas
    print("\n5. CHECKING TABLE SCHEMAS...")

    if 'plans' in existing_tables:
        try:
            query = "PRAGMA table_info(plans)"
            schema = db_handler.execute_query(query)
            print(f"   plans table columns: {[col.get('name') for col in schema]}")
        except Exception as e:
            print(f"   plans schema: ERROR - {e}")

    if 'lgraph_plans' in existing_tables:
        try:
            query = "PRAGMA table_info(lgraph_plans)"
            schema = db_handler.execute_query(query)
            print(f"   lgraph_plans table columns: {[col.get('name') for col in schema]}")
        except Exception as e:
            print(f"   lgraph_plans schema: ERROR - {e}")

    # 6. Test monitoring queries
    print("\n6. TESTING MONITORING QUERIES...")

    from datetime import datetime, timedelta
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    if 'plans' in existing_tables:
        try:
            query = "SELECT COUNT(*) as count FROM plans WHERE created_at >= ?"
            result = db_handler.execute_query(query, (today_start,))
            count = result[0].get('count', 0) if result else 0
            print(f"   Plans created today: {count}")
        except Exception as e:
            print(f"   Plans query: ERROR - {e}")

    if 'lgraph_plans' in existing_tables:
        try:
            query = "SELECT COUNT(*) as count FROM lgraph_plans WHERE created_at >= ?"
            result = db_handler.execute_query(query, (today_start,))
            count = result[0].get('count', 0) if result else 0
            print(f"   LangGraph plans created today: {count}")
        except Exception as e:
            print(f"   LangGraph plans query: ERROR - {e}")

    # 7. Summary and recommendations
    print("\n" + "=" * 60)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 60)

    if len(missing_tables) > 0:
        print(f"\n⚠️  MISSING TABLES: {', '.join(missing_tables)}")
        print("   → These tables need to be created in your database")

    if 'plans' not in existing_tables and 'lgraph_plans' not in existing_tables:
        print("\n❌ CRITICAL: No plan tables exist!")
        print("   → Plans cannot be stored anywhere")
        print("   → Check your database initialization")

    if 'plans' in existing_tables:
        try:
            count = db_handler.count_all('plans')
            if count == 0:
                print("\n⚠️  'plans' table is EMPTY")
                print("   → Regular DAG plans are not being created")
                print("   → Check planner_routes.py create_plan logic")
        except:
            pass

    if 'lgraph_plans' in existing_tables:
        try:
            count = db_handler.count_all('lgraph_plans')
            if count == 0:
                print("\n⚠️  'lgraph_plans' table is EMPTY")
                print("   → LangGraph plans are not being created")
                print("   → Check lgraph_planner_routes.py create_plan logic")
        except:
            pass

    print("\n" + "=" * 60)
    print("END OF DIAGNOSTIC REPORT")
    print("=" * 60 + "\n")

# HOW TO USE THIS SCRIPT:
#
# Option 1: Add as Flask route
# @app.route('/admin/diagnose')
# def diagnose():
#     from db.database_call_handler import get_database_handler
#     db_handler = get_database_handler()
#     diagnose_monitoring_issue(db_handler)
#     return "Check console output"
#
# Option 2: Run directly
if __name__ == "__main__":
     from db.database_call_handler import get_database_handler
     from db.database import get_db
     get_db()
     db_handler = get_database_handler()
     diagnose_monitoring_issue(db_handler)