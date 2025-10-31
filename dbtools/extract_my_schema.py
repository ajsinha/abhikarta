"""
Practical Schema Extraction Script
Works with your database files directly

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def extract_and_save_schema(db_path, output_path, include_drop=True, verbose=True):
    """
    Extract schema from database and save to SQL file
    
    Args:
        db_path: Path to SQLite database
        output_path: Path for output SQL file
        include_drop: Include DROP TABLE statements
        verbose: Print progress information
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"DATABASE SCHEMA EXTRACTION")
        print(f"{'='*70}")
        print(f"Source Database: {db_path}")
        print(f"Output File: {output_path}")
        print(f"Include DROP statements: {include_drop}")
        print(f"{'='*70}\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        sql_output = []
        
        # Add header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql_output.append(f"""-- ============================================
-- Database Schema Export
-- ============================================
-- Source: {db_path}
-- Generated: {timestamp}
-- ============================================

""")
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        if verbose:
            print(f"📋 Found {len(tables)} tables:")
            for i, table in enumerate(tables, 1):
                print(f"   {i:2d}. {table}")
            print()
        
        # Process each table
        for table_num, table_name in enumerate(tables, 1):
            if verbose:
                print(f"⚙️  Processing table {table_num}/{len(tables)}: {table_name}")
            
            # Table header
            sql_output.append(f"""
-- ============================================
-- Table: {table_name}
-- ============================================
""")
            
            # DROP statement
            if include_drop:
                sql_output.append(f"DROP TABLE IF EXISTS {table_name};")
            
            # CREATE TABLE statement
            cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            
            create_result = cursor.fetchone()
            if create_result and create_result[0]:
                sql_output.append(f"{create_result[0]};")
            
            # Get column info for documentation
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if verbose:
                print(f"   └─ {len(columns)} columns")
            
            # Add comment with column list
            sql_output.append(f"\n-- Columns: {', '.join([col[1] for col in columns])}")
            
            # Get indexes
            cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='index' 
                AND tbl_name=? 
                AND sql IS NOT NULL
                ORDER BY name
            """, (table_name,))
            
            indexes = cursor.fetchall()
            if indexes:
                sql_output.append(f"\n-- Indexes for {table_name}:")
                for idx in indexes:
                    if idx[0]:
                        sql_output.append(f"{idx[0]};")
                
                if verbose:
                    print(f"   └─ {len(indexes)} indexes")
            
            # Get triggers
            cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='trigger' 
                AND tbl_name=?
                ORDER BY name
            """, (table_name,))
            
            triggers = cursor.fetchall()
            if triggers:
                sql_output.append(f"\n-- Triggers for {table_name}:")
                for trigger in triggers:
                    if trigger[0]:
                        sql_output.append(f"{trigger[0]};")
                
                if verbose:
                    print(f"   └─ {len(triggers)} triggers")
        
        # Get views
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='view'
            ORDER BY name
        """)
        
        views = cursor.fetchall()
        
        if views:
            if verbose:
                print(f"\n📊 Found {len(views)} views")
            
            sql_output.append(f"""

-- ============================================
-- Views ({len(views)} total)
-- ============================================
""")
            
            for view_name, view_sql in views:
                if include_drop:
                    sql_output.append(f"DROP VIEW IF EXISTS {view_name};")
                sql_output.append(f"{view_sql};")
                sql_output.append("")
        
        # Add footer
        sql_output.append(f"""
-- ============================================
-- End of schema export
-- Total: {len(tables)} tables, {len(views)} views
-- ============================================
""")
        
        # Close database
        conn.close()
        
        # Write to file
        schema_text = "\n".join(sql_output)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(schema_text)
        
        if verbose:
            file_size = Path(output_path).stat().st_size
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS!")
            print(f"{'='*70}")
            print(f"Schema exported to: {output_path}")
            print(f"File size: {file_size:,} bytes")
            print(f"Total tables: {len(tables)}")
            print(f"Total views: {len(views)}")
            print(f"\n💡 You can now run this SQL file on any SQLite database to recreate the schema.")
            print(f"{'='*70}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        return False


def quick_table_summary(db_path):
    """
    Print a quick summary of database tables
    
    Args:
        db_path: Path to SQLite database
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n{'='*70}")
        print(f"DATABASE TABLE SUMMARY: {db_path}")
        print(f"{'='*70}\n")
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"{'Table Name':<30} {'Columns':<10} {'Has Indexes':<12} {'Has Triggers'}")
        print("-" * 70)
        
        for table in tables:
            # Get column count
            cursor.execute(f"PRAGMA table_info({table})")
            col_count = len(cursor.fetchall())
            
            # Check for indexes
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='index' AND tbl_name=? AND sql IS NOT NULL
            """, (table,))
            has_indexes = cursor.fetchone()[0] > 0
            
            # Check for triggers
            cursor.execute("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='trigger' AND tbl_name=?
            """, (table,))
            has_triggers = cursor.fetchone()[0] > 0
            
            print(f"{table:<30} {col_count:<10} {str(has_indexes):<12} {has_triggers}")
        
        print(f"\nTotal Tables: {len(tables)}")
        print(f"{'='*70}\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Configuration
    DATABASE_PATH = "/home/ashutosh/PycharmProjects/abhikarta/data/abhikarta.db"  # Change this to your database path
    OUTPUT_SQL_FILE = "/home/ashutosh/PycharmProjects/abhikarta/data/abhikarta.db.sql"
    INCLUDE_DROP_STATEMENTS = True
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                  DATABASE SCHEMA EXTRACTOR                         ║
║                                                                    ║
║  This script extracts your database schema and generates          ║
║  executable SQL that can be run on any SQLite database.           ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if database exists
    if not Path(DATABASE_PATH).exists():
        print(f"❌ Database file not found: {DATABASE_PATH}")
        print(f"\n💡 Please update the DATABASE_PATH variable in this script.")
        sys.exit(1)
    
    # Option 1: Quick summary
    quick_table_summary(DATABASE_PATH)
    
    # Option 2: Extract full schema
    print("\n🚀 Starting schema extraction...\n")
    success = extract_and_save_schema(
        db_path=DATABASE_PATH,
        output_path=OUTPUT_SQL_FILE,
        include_drop=INCLUDE_DROP_STATEMENTS,
        verbose=True
    )
    
    if success:
        print("✅ All done! Your schema is ready to use.\n")
    else:
        print("❌ Schema extraction failed.\n")
        sys.exit(1)
