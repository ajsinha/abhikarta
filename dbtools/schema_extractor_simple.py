"""
Simple Database Schema Extractor - Library Usage Examples
Quick and easy database schema extraction

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import sqlite3
from pathlib import Path


def extract_sqlite_schema(db_path: str, include_drop: bool = False) -> str:
    """
    Extract complete SQLite database schema as executable SQL
    
    Args:
        db_path: Path to SQLite database file
        include_drop: Whether to include DROP TABLE statements
        
    Returns:
        Complete SQL schema as string
    
    Example:
        >>> schema_sql = extract_sqlite_schema('mydb.sqlite')
        >>> with open('schema.sql', 'w') as f:
        ...     f.write(schema_sql)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    sql_parts = []
    
    # Header
    sql_parts.append(f"-- Schema for: {db_path}\n")
    
    # Get all tables
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    # Extract each table
    for table in tables:
        sql_parts.append(f"\n-- Table: {table}")
        
        if include_drop:
            sql_parts.append(f"DROP TABLE IF EXISTS {table};")
        
        # Get CREATE TABLE statement
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        create_sql = cursor.fetchone()
        if create_sql:
            sql_parts.append(f"{create_sql[0]};")
        
        # Get indexes
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='index' 
            AND tbl_name=? 
            AND sql IS NOT NULL
        """, (table,))
        indexes = cursor.fetchall()
        for idx in indexes:
            if idx[0]:
                sql_parts.append(f"{idx[0]};")
    
    # Get views
    cursor.execute("""
        SELECT name, sql FROM sqlite_master 
        WHERE type='view'
        ORDER BY name
    """)
    views = cursor.fetchall()
    
    if views:
        sql_parts.append("\n-- Views")
        for view_name, view_sql in views:
            if include_drop:
                sql_parts.append(f"DROP VIEW IF EXISTS {view_name};")
            sql_parts.append(f"{view_sql};")
    
    conn.close()
    return "\n".join(sql_parts)


def extract_table_schema(db_path: str, table_name: str) -> str:
    """
    Extract schema for a single table
    
    Args:
        db_path: Path to SQLite database file
        table_name: Name of the table
        
    Returns:
        CREATE TABLE statement as string
    
    Example:
        >>> table_sql = extract_table_schema('mydb.sqlite', 'users')
        >>> print(table_sql)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None


def get_table_columns(db_path: str, table_name: str) -> list:
    """
    Get column information for a table
    
    Args:
        db_path: Path to SQLite database file
        table_name: Name of the table
        
    Returns:
        List of dictionaries with column information
    
    Example:
        >>> columns = get_table_columns('mydb.sqlite', 'users')
        >>> for col in columns:
        ...     print(f"{col['name']}: {col['type']}")
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    
    columns = []
    for row in cursor.fetchall():
        columns.append({
            'name': row[1],
            'type': row[2],
            'notnull': bool(row[3]),
            'default': row[4],
            'primary_key': bool(row[5])
        })
    
    conn.close()
    return columns


def list_tables(db_path: str) -> list:
    """
    List all tables in the database
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        List of table names
    
    Example:
        >>> tables = list_tables('mydb.sqlite')
        >>> print(f"Found {len(tables)} tables: {', '.join(tables)}")
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return tables


def export_schema_to_file(db_path: str, output_file: str, include_drop: bool = False):
    """
    Export database schema directly to a file
    
    Args:
        db_path: Path to SQLite database file
        output_file: Path to output SQL file
        include_drop: Whether to include DROP TABLE statements
    
    Example:
        >>> export_schema_to_file('mydb.sqlite', 'schema.sql', include_drop=True)
    """
    schema_sql = extract_sqlite_schema(db_path, include_drop)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(schema_sql)
    
    print(f"✅ Schema exported to: {output_file}")


def compare_schemas(db1_path: str, db2_path: str) -> dict:
    """
    Compare schemas of two databases
    
    Args:
        db1_path: Path to first database
        db2_path: Path to second database
        
    Returns:
        Dictionary with differences
    
    Example:
        >>> diff = compare_schemas('db1.sqlite', 'db2.sqlite')
        >>> print(f"Tables only in db1: {diff['only_in_db1']}")
    """
    tables1 = set(list_tables(db1_path))
    tables2 = set(list_tables(db2_path))
    
    return {
        'only_in_db1': list(tables1 - tables2),
        'only_in_db2': list(tables2 - tables1),
        'common': list(tables1 & tables2)
    }


# ============================================
# USAGE EXAMPLES
# ============================================

def example_basic_extraction():
    """Example 1: Basic schema extraction"""
    print("Example 1: Basic Schema Extraction")
    print("-" * 50)
    
    # Extract entire database schema
    schema = extract_sqlite_schema('mydb.sqlite')
    
    # Save to file
    with open('schema.sql', 'w') as f:
        f.write(schema)
    
    print("✅ Schema saved to schema.sql")


def example_with_drop_statements():
    """Example 2: Extract with DROP statements"""
    print("\nExample 2: With DROP Statements")
    print("-" * 50)
    
    schema = extract_sqlite_schema('mydb.sqlite', include_drop=True)
    
    with open('schema_with_drop.sql', 'w') as f:
        f.write(schema)
    
    print("✅ Schema with DROP statements saved")


def example_single_table():
    """Example 3: Extract single table"""
    print("\nExample 3: Single Table Extraction")
    print("-" * 50)
    
    table_sql = extract_table_schema('mydb.sqlite', 'users')
    
    if table_sql:
        print(f"CREATE TABLE statement:\n{table_sql}")
    else:
        print("Table not found")


def example_table_info():
    """Example 4: Get table column information"""
    print("\nExample 4: Table Column Information")
    print("-" * 50)
    
    columns = get_table_columns('mydb.sqlite', 'users')
    
    print(f"{'Column':<20} {'Type':<15} {'Not Null':<10} {'Primary Key'}")
    print("-" * 65)
    
    for col in columns:
        print(f"{col['name']:<20} {col['type']:<15} {col['notnull']!s:<10} {col['primary_key']}")


def example_list_all_tables():
    """Example 5: List all tables"""
    print("\nExample 5: List All Tables")
    print("-" * 50)
    
    tables = list_tables('mydb.sqlite')
    
    print(f"Found {len(tables)} tables:")
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")


def example_export_helper():
    """Example 6: Use export helper function"""
    print("\nExample 6: Export Helper Function")
    print("-" * 50)
    
    export_schema_to_file('mydb.sqlite', 'exported_schema.sql', include_drop=True)


def example_compare_databases():
    """Example 7: Compare two databases"""
    print("\nExample 7: Compare Database Schemas")
    print("-" * 50)
    
    diff = compare_schemas('db1.sqlite', 'db2.sqlite')
    
    print(f"Tables only in db1: {diff['only_in_db1']}")
    print(f"Tables only in db2: {diff['only_in_db2']}")
    print(f"Common tables: {diff['common']}")


def example_recreate_database():
    """Example 8: Recreate database from schema"""
    print("\nExample 8: Recreate Database from Schema")
    print("-" * 50)
    
    # Step 1: Extract schema from source
    schema = extract_sqlite_schema('source.sqlite')
    
    # Step 2: Save to file
    with open('schema.sql', 'w') as f:
        f.write(schema)
    
    # Step 3: Create new database and apply schema
    import sqlite3
    new_conn = sqlite3.connect('destination.sqlite')
    new_conn.executescript(schema)
    new_conn.close()
    
    print("✅ Database recreated successfully")


def example_generate_migration():
    """Example 9: Generate migration script"""
    print("\nExample 9: Generate Migration Script")
    print("-" * 50)
    
    # Get tables from both databases
    old_tables = set(list_tables('old_db.sqlite'))
    new_tables = set(list_tables('new_db.sqlite'))
    
    # Generate migration
    migration = []
    migration.append("-- Migration Script\n")
    
    # New tables
    added_tables = new_tables - old_tables
    for table in added_tables:
        table_sql = extract_table_schema('new_db.sqlite', table)
        migration.append(f"-- Add new table: {table}")
        migration.append(f"{table_sql};\n")
    
    # Removed tables
    removed_tables = old_tables - new_tables
    for table in removed_tables:
        migration.append(f"-- Remove table: {table}")
        migration.append(f"DROP TABLE IF EXISTS {table};\n")
    
    # Save migration
    with open('migration.sql', 'w') as f:
        f.write('\n'.join(migration))
    
    print("✅ Migration script generated")


if __name__ == "__main__":
    print("="*60)
    print("DATABASE SCHEMA EXTRACTOR - USAGE EXAMPLES")
    print("="*60)
    
    # Run examples (comment out as needed)
    # example_basic_extraction()
    # example_with_drop_statements()
    # example_single_table()
    # example_table_info()
    # example_list_all_tables()
    # example_export_helper()
    # example_compare_databases()
    # example_recreate_database()
    # example_generate_migration()
    
    print("\n💡 Tip: Uncomment the examples you want to run!")
