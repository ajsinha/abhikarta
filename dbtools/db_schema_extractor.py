"""
Database Schema Extractor
Extracts database schema and generates executable SQL DDL statements

Supports: SQLite, PostgreSQL, MySQL, SQL Server

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import sqlite3
import argparse
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseSchemaExtractor:
    """Extract database schema and generate SQL DDL"""
    
    def __init__(self, db_path: str, db_type: str = 'sqlite'):
        """
        Initialize the schema extractor
        
        Args:
            db_path: Path to database file (SQLite) or connection string
            db_type: Type of database (sqlite, postgresql, mysql, mssql)
        """
        self.db_path = db_path
        self.db_type = db_type.lower()
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database"""
        if self.db_type == 'sqlite':
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        else:
            raise NotImplementedError(f"Database type {self.db_type} not yet implemented")
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        if self.db_type == 'sqlite':
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            return [row[0] for row in self.cursor.fetchall()]
        return []
    
    def get_table_schema(self, table_name: str) -> str:
        """
        Get the CREATE TABLE statement for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            SQL CREATE TABLE statement
        """
        if self.db_type == 'sqlite':
            self.cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (table_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        return None
    
    def get_indexes(self, table_name: str) -> List[str]:
        """
        Get all indexes for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of CREATE INDEX statements
        """
        if self.db_type == 'sqlite':
            self.cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='index' 
                AND tbl_name=? 
                AND sql IS NOT NULL
                ORDER BY name
            """, (table_name,))
            return [row[0] for row in self.cursor.fetchall() if row[0]]
        return []
    
    def get_triggers(self, table_name: str) -> List[str]:
        """
        Get all triggers for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of CREATE TRIGGER statements
        """
        if self.db_type == 'sqlite':
            self.cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='trigger' 
                AND tbl_name=?
                ORDER BY name
            """, (table_name,))
            return [row[0] for row in self.cursor.fetchall() if row[0]]
        return []
    
    def get_views(self) -> List[tuple]:
        """
        Get all views in the database
        
        Returns:
            List of tuples (view_name, create_statement)
        """
        if self.db_type == 'sqlite':
            self.cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='view'
                ORDER BY name
            """)
            return [(row[0], row[1]) for row in self.cursor.fetchall()]
        return []
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get detailed column information for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information dictionaries
        """
        if self.db_type == 'sqlite':
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in self.cursor.fetchall():
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'default': row[4],
                    'pk': row[5]
                })
            return columns
        return []
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get foreign key information for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of foreign key information dictionaries
        """
        if self.db_type == 'sqlite':
            self.cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            fks = []
            for row in self.cursor.fetchall():
                fks.append({
                    'id': row[0],
                    'seq': row[1],
                    'table': row[2],
                    'from': row[3],
                    'to': row[4],
                    'on_update': row[5],
                    'on_delete': row[6],
                    'match': row[7]
                })
            return fks
        return []
    
    def generate_schema_sql(self, 
                           include_drop: bool = False,
                           include_indexes: bool = True,
                           include_triggers: bool = True,
                           include_views: bool = True,
                           include_comments: bool = True) -> str:
        """
        Generate complete schema SQL
        
        Args:
            include_drop: Include DROP TABLE IF EXISTS statements
            include_indexes: Include CREATE INDEX statements
            include_triggers: Include CREATE TRIGGER statements
            include_views: Include CREATE VIEW statements
            include_comments: Include SQL comments
            
        Returns:
            Complete SQL schema as string
        """
        sql_parts = []
        
        # Header comment
        if include_comments:
            sql_parts.append(self._generate_header())
        
        # Get all tables
        tables = self.get_tables()
        
        if include_comments:
            sql_parts.append(f"\n-- Found {len(tables)} tables\n")
        
        # Generate table schemas
        for table in tables:
            if include_comments:
                sql_parts.append(f"\n-- ============================================")
                sql_parts.append(f"-- Table: {table}")
                sql_parts.append(f"-- ============================================\n")
            
            # DROP statement
            if include_drop:
                sql_parts.append(f"DROP TABLE IF EXISTS {table};")
            
            # CREATE TABLE statement
            create_sql = self.get_table_schema(table)
            if create_sql:
                sql_parts.append(f"{create_sql};")
            
            # Indexes
            if include_indexes:
                indexes = self.get_indexes(table)
                if indexes:
                    if include_comments:
                        sql_parts.append(f"\n-- Indexes for {table}")
                    for idx_sql in indexes:
                        sql_parts.append(f"{idx_sql};")
            
            # Triggers
            if include_triggers:
                triggers = self.get_triggers(table)
                if triggers:
                    if include_comments:
                        sql_parts.append(f"\n-- Triggers for {table}")
                    for trigger_sql in triggers:
                        sql_parts.append(f"{trigger_sql};")
            
            sql_parts.append("")  # Empty line between tables
        
        # Views
        if include_views:
            views = self.get_views()
            if views:
                if include_comments:
                    sql_parts.append(f"\n-- ============================================")
                    sql_parts.append(f"-- Views ({len(views)} total)")
                    sql_parts.append(f"-- ============================================\n")
                
                for view_name, view_sql in views:
                    if include_drop:
                        sql_parts.append(f"DROP VIEW IF EXISTS {view_name};")
                    sql_parts.append(f"{view_sql};")
                    sql_parts.append("")
        
        # Footer
        if include_comments:
            sql_parts.append(self._generate_footer())
        
        return "\n".join(sql_parts)
    
    def _generate_header(self) -> str:
        """Generate SQL header comment"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""-- ============================================
-- Database Schema Export
-- ============================================
-- Database: {self.db_path}
-- Type: {self.db_type.upper()}
-- Generated: {timestamp}
-- ============================================
"""
    
    def _generate_footer(self) -> str:
        """Generate SQL footer comment"""
        return f"""-- ============================================
-- End of schema export
-- ============================================
"""
    
    def generate_table_documentation(self, table_name: str) -> str:
        """
        Generate human-readable documentation for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Formatted documentation string
        """
        docs = []
        docs.append(f"\n{'='*60}")
        docs.append(f"TABLE: {table_name}")
        docs.append(f"{'='*60}\n")
        
        # Column information
        columns = self.get_table_info(table_name)
        docs.append("COLUMNS:")
        docs.append(f"{'Name':<20} {'Type':<15} {'Null':<6} {'PK':<4} {'Default':<15}")
        docs.append("-" * 60)
        
        for col in columns:
            null_str = "NO" if col['notnull'] else "YES"
            pk_str = "YES" if col['pk'] else "NO"
            default_str = str(col['default']) if col['default'] is not None else ""
            docs.append(f"{col['name']:<20} {col['type']:<15} {null_str:<6} {pk_str:<4} {default_str:<15}")
        
        # Foreign keys
        fks = self.get_foreign_keys(table_name)
        if fks:
            docs.append("\nFOREIGN KEYS:")
            for fk in fks:
                docs.append(f"  {fk['from']} -> {fk['table']}.{fk['to']}")
        
        # Indexes
        indexes = self.get_indexes(table_name)
        if indexes:
            docs.append("\nINDEXES:")
            for idx in indexes:
                docs.append(f"  {idx}")
        
        return "\n".join(docs)
    
    def export_to_file(self, output_file: str, **kwargs):
        """
        Export schema to a SQL file
        
        Args:
            output_file: Path to output SQL file
            **kwargs: Additional arguments for generate_schema_sql()
        """
        schema_sql = self.generate_schema_sql(**kwargs)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(schema_sql)
        
        print(f"✅ Schema exported to: {output_file}")
        
    def export_documentation(self, output_file: str):
        """
        Export human-readable documentation to a text file
        
        Args:
            output_file: Path to output documentation file
        """
        docs = []
        docs.append(self._generate_header())
        
        tables = self.get_tables()
        docs.append(f"\nDatabase contains {len(tables)} tables:\n")
        
        for table in tables:
            docs.append(self.generate_table_documentation(table))
        
        docs.append(f"\n{self._generate_footer()}")
        
        doc_text = "\n".join(docs)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(doc_text)
        
        print(f"✅ Documentation exported to: {output_file}")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Extract database schema and generate SQL DDL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract SQLite schema to SQL file
  python db_schema_extractor.py mydb.sqlite -o schema.sql
  
  # Extract with DROP statements
  python db_schema_extractor.py mydb.sqlite -o schema.sql --drop
  
  # Extract without indexes and triggers
  python db_schema_extractor.py mydb.sqlite -o schema.sql --no-indexes --no-triggers
  
  # Generate documentation
  python db_schema_extractor.py mydb.sqlite --doc schema_doc.txt
  
  # Print to console
  python db_schema_extractor.py mydb.sqlite --print
        """
    )
    
    parser.add_argument('database', help='Database file path or connection string')
    parser.add_argument('-o', '--output', help='Output SQL file path')
    parser.add_argument('-t', '--type', default='sqlite', 
                       choices=['sqlite', 'postgresql', 'mysql', 'mssql'],
                       help='Database type (default: sqlite)')
    parser.add_argument('--drop', action='store_true',
                       help='Include DROP TABLE statements')
    parser.add_argument('--no-indexes', action='store_true',
                       help='Exclude indexes from output')
    parser.add_argument('--no-triggers', action='store_true',
                       help='Exclude triggers from output')
    parser.add_argument('--no-views', action='store_true',
                       help='Exclude views from output')
    parser.add_argument('--no-comments', action='store_true',
                       help='Exclude SQL comments from output')
    parser.add_argument('--doc', help='Export documentation to text file')
    parser.add_argument('--print', action='store_true',
                       help='Print schema to console')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.output and not args.doc and not args.print:
        parser.error("Must specify at least one of: --output, --doc, or --print")
    
    try:
        # Create extractor
        extractor = DatabaseSchemaExtractor(args.database, args.type)
        extractor.connect()
        
        print(f"📊 Analyzing database: {args.database}")
        
        tables = extractor.get_tables()
        print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
        
        # Generate schema options
        schema_options = {
            'include_drop': args.drop,
            'include_indexes': not args.no_indexes,
            'include_triggers': not args.no_triggers,
            'include_views': not args.no_views,
            'include_comments': not args.no_comments
        }
        
        # Export SQL
        if args.output:
            extractor.export_to_file(args.output, **schema_options)
        
        # Export documentation
        if args.doc:
            extractor.export_documentation(args.doc)
        
        # Print to console
        if args.print:
            schema_sql = extractor.generate_schema_sql(**schema_options)
            print("\n" + "="*60)
            print("SCHEMA SQL")
            print("="*60 + "\n")
            print(schema_sql)
        
        extractor.disconnect()
        print("\n✅ Extraction complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
