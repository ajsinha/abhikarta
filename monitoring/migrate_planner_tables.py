"""
Database Migration Script - Add Plans and Planner Conversations Tables
Run this to add monitoring support for planner

© 2025-2030 Ashutosh Sinha
"""

from db.database import get_db


def migrate_add_planner_tables():
    """Add plans and planner_conversations tables"""
    db = get_db()

    print("Adding planner monitoring tables...")

    # Plans table
    db.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            request TEXT,
            plan_json TEXT,
            status TEXT DEFAULT 'pending_approval',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            approved_at TEXT,
            rejected_at TEXT,
            rejection_reason TEXT
        )
    """)
    print("✓ Created plans table")

    # Planner conversations table
    db.execute("""
        CREATE TABLE IF NOT EXISTS planner_conversations (
            conversation_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            message TEXT,
            response TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Created planner_conversations table")

    print("\nMigration complete!")
    print("\nYou can now use the planner monitoring features.")


if __name__ == '__main__':
    migrate_add_planner_tables()