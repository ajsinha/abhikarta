"""
Database Schema Diff & Migration Generator
Compare two database schemas and generate migration scripts

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import sqlite3
import sys
from datetime import datetime
from typing import Dict, List, Set, Tuple


class SchemaDiff:
    """Compare two database schemas and generate migration SQL"""
    
    def __init__(self, old_db: str, new_db: str):
        """
        Initialize schema comparison
        
        Args:
            old_db: Path to old/source database
            new_db: Path to new/target database
        """
        self.old_db = old_db
        self.new_db = new_db
    
    def get_tables(self, db_path: str) -> Set[str]:
        """Get set of all table names"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
        """)
        
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        return tables
    
    def get_table_schema(self, db_path: str, table_name: str) -> str:
        """Get CREATE TABLE statement"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_columns(self, db_path: str, table_name: str) -> Dict[str, Dict]:
        """Get column information for a table"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        
        columns = {}
        for row in cursor.fetchall():
            columns[row[1]] = {
                'type': row[2],
                'notnull': bool(row[3]),
                'default': row[4],
                'pk': bool(row[5])
            }
        
        conn.close()
        return columns
    
    def get_indexes(self, db_path: str, table_name: str) -> Dict[str, str]:
        """Get indexes for a table"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, sql FROM sqlite_master 
            WHERE type='index' 
            AND tbl_name=? 
            AND sql IS NOT NULL
        """, (table_name,))
        
        indexes = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return indexes
    
    def compare_tables(self) -> Dict[str, any]:
        """
        Compare table structures between databases
        
        Returns:
            Dictionary with differences
        """
        old_tables = self.get_tables(self.old_db)
        new_tables = self.get_tables(self.new_db)
        
        return {
            'added_tables': new_tables - old_tables,
            'removed_tables': old_tables - new_tables,
            'common_tables': old_tables & new_tables,
            'all_old_tables': old_tables,
            'all_new_tables': new_tables
        }
    
    def compare_table_columns(self, table_name: str) -> Dict[str, any]:
        """
        Compare columns between same table in both databases
        
        Args:
            table_name: Name of the table to compare
            
        Returns:
            Dictionary with column differences
        """
        old_cols = self.get_columns(self.old_db, table_name)
        new_cols = self.get_columns(self.new_db, table_name)
        
        old_col_names = set(old_cols.keys())
        new_col_names = set(new_cols.keys())
        
        added = new_col_names - old_col_names
        removed = old_col_names - new_col_names
        common = old_col_names & new_col_names
        
        # Check for modified columns
        modified = {}
        for col_name in common:
            if old_cols[col_name] != new_cols[col_name]:
                modified[col_name] = {
                    'old': old_cols[col_name],
                    'new': new_cols[col_name]
                }
        
        return {
            'added_columns': added,
            'removed_columns': removed,
            'modified_columns': modified,
            'all_old_columns': old_cols,
            'all_new_columns': new_cols
        }
    
    def generate_migration_sql(self, 
                               include_drops: bool = False,
                               include_data_migration: bool = False) -> str:
        """
        Generate SQL migration script
        
        Args:
            include_drops: Include DROP statements for removed tables
            include_data_migration: Include data migration for modified tables
            
        Returns:
            SQL migration script
        """
        migration_parts = []
        
        # Header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        migration_parts.append(f"""-- ============================================
-- Database Migration Script
-- ============================================
-- From: {self.old_db}
-- To: {self.new_db}
-- Generated: {timestamp}
-- ============================================

-- NOTE: This is a SQLite migration script.
-- SQLite has limited ALTER TABLE support.
-- Some changes may require table recreation.

""")
        
        # Compare tables
        table_diff = self.compare_tables()
        
        # Added tables
        if table_diff['added_tables']:
            migration_parts.append("""
-- ============================================
-- NEW TABLES
-- ============================================
""")
            
            for table in sorted(table_diff['added_tables']):
                schema = self.get_table_schema(self.new_db, table)
                migration_parts.append(f"-- Add table: {table}")
                migration_parts.append(f"{schema};")
                
                # Add indexes
                indexes = self.get_indexes(self.new_db, table)
                for idx_name, idx_sql in indexes.items():
                    migration_parts.append(f"{idx_sql};")
                
                migration_parts.append("")
        
        # Removed tables
        if table_diff['removed_tables'] and include_drops:
            migration_parts.append("""
-- ============================================
-- REMOVED TABLES
-- ============================================
""")
            
            for table in sorted(table_diff['removed_tables']):
                migration_parts.append(f"-- Remove table: {table}")
                migration_parts.append(f"DROP TABLE IF EXISTS {table};")
                migration_parts.append("")
        
        # Modified tables
        if table_diff['common_tables']:
            migration_parts.append("""
-- ============================================
-- MODIFIED TABLES
-- ============================================
""")
            
            for table in sorted(table_diff['common_tables']):
                col_diff = self.compare_table_columns(table)
                
                # Check if table has changes
                has_changes = (col_diff['added_columns'] or 
                             col_diff['removed_columns'] or 
                             col_diff['modified_columns'])
                
                if has_changes:
                    migration_parts.append(f"\n-- Table: {table}")
                    migration_parts.append(f"-- Changes detected in structure")
                    
                    # Added columns
                    if col_diff['added_columns']:
                        migration_parts.append(f"-- Added columns: {', '.join(col_diff['added_columns'])}")
                        
                        for col_name in sorted(col_diff['added_columns']):
                            col_info = col_diff['all_new_columns'][col_name]
                            col_def = self._format_column_definition(col_name, col_info)
                            migration_parts.append(f"ALTER TABLE {table} ADD COLUMN {col_def};")
                    
                    # Removed columns
                    if col_diff['removed_columns']:
                        migration_parts.append(f"-- Removed columns: {', '.join(col_diff['removed_columns'])}")
                        migration_parts.append(f"-- WARNING: SQLite does not support DROP COLUMN directly")
                        migration_parts.append(f"-- You may need to recreate the table: {table}")
                    
                    # Modified columns
                    if col_diff['modified_columns']:
                        migration_parts.append(f"-- Modified columns: {', '.join(col_diff['modified_columns'].keys())}")
                        migration_parts.append(f"-- WARNING: SQLite does not support ALTER COLUMN directly")
                        migration_parts.append(f"-- You may need to recreate the table: {table}")
                        
                        # Show what changed
                        for col_name, changes in col_diff['modified_columns'].items():
                            migration_parts.append(f"-- {col_name}: {changes['old']} -> {changes['new']}")
                    
                    migration_parts.append("")
                    
                    # If table needs recreation
                    if col_diff['removed_columns'] or col_diff['modified_columns']:
                        migration_parts.append(self._generate_table_recreation(table))
        
        # Compare indexes
        migration_parts.append(self._generate_index_migration(table_diff['common_tables']))
        
        # Footer
        migration_parts.append("""
-- ============================================
-- End of migration script
-- ============================================
-- Remember to:
-- 1. Backup your database before running this script
-- 2. Test in a development environment first
-- 3. Review any manual intervention notes above
-- ============================================
""")
        
        return "\n".join(migration_parts)
    
    def _format_column_definition(self, col_name: str, col_info: Dict) -> str:
        """Format column definition for ALTER TABLE ADD COLUMN"""
        parts = [col_name, col_info['type']]
        
        if col_info['notnull']:
            parts.append('NOT NULL')
        
        if col_info['default'] is not None:
            parts.append(f"DEFAULT {col_info['default']}")
        
        return " ".join(parts)
    
    def _generate_table_recreation(self, table_name: str) -> str:
        """
        Generate SQL to recreate a table (for complex changes)
        
        Args:
            table_name: Name of the table
            
        Returns:
            SQL script for table recreation
        """
        old_cols = self.get_columns(self.old_db, table_name)
        new_cols = self.get_columns(self.new_db, table_name)
        new_schema = self.get_table_schema(self.new_db, table_name)
        
        # Find common columns for data migration
        common_cols = set(old_cols.keys()) & set(new_cols.keys())
        col_list = ", ".join(sorted(common_cols))
        
        recreation_sql = f"""
-- Complex changes require table recreation for: {table_name}
-- Step 1: Rename old table
ALTER TABLE {table_name} RENAME TO {table_name}_old;

-- Step 2: Create new table with updated structure
{new_schema};

-- Step 3: Copy data from old table (common columns only)
INSERT INTO {table_name} ({col_list})
SELECT {col_list}
FROM {table_name}_old;

-- Step 4: Drop old table
DROP TABLE {table_name}_old;

-- Step 5: Recreate indexes (see index migration section)
"""
        return recreation_sql
    
    def _generate_index_migration(self, common_tables: Set[str]) -> str:
        """Generate index migration SQL"""
        migration = []
        migration.append("""
-- ============================================
-- INDEX CHANGES
-- ============================================
""")
        
        for table in sorted(common_tables):
            old_indexes = self.get_indexes(self.old_db, table)
            new_indexes = self.get_indexes(self.new_db, table)
            
            old_idx_names = set(old_indexes.keys())
            new_idx_names = set(new_indexes.keys())
            
            added = new_idx_names - old_idx_names
            removed = old_idx_names - new_idx_names
            
            if added or removed:
                migration.append(f"\n-- Table: {table}")
                
                # Removed indexes
                for idx_name in sorted(removed):
                    migration.append(f"DROP INDEX IF EXISTS {idx_name};")
                
                # Added indexes
                for idx_name in sorted(added):
                    migration.append(f"{new_indexes[idx_name]};")
        
        return "\n".join(migration)
    
    def generate_diff_report(self) -> str:
        """
        Generate human-readable difference report
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("="*70)
        report.append("DATABASE SCHEMA COMPARISON REPORT")
        report.append("="*70)
        report.append(f"Old Database: {self.old_db}")
        report.append(f"New Database: {self.new_db}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*70)
        
        # Table comparison
        table_diff = self.compare_tables()
        
        report.append(f"\n📊 TABLES")
        report.append(f"  Total in old: {len(table_diff['all_old_tables'])}")
        report.append(f"  Total in new: {len(table_diff['all_new_tables'])}")
        report.append(f"  Added: {len(table_diff['added_tables'])}")
        report.append(f"  Removed: {len(table_diff['removed_tables'])}")
        report.append(f"  Common: {len(table_diff['common_tables'])}")
        
        if table_diff['added_tables']:
            report.append(f"\n✅ ADDED TABLES ({len(table_diff['added_tables'])})")
            for table in sorted(table_diff['added_tables']):
                report.append(f"  + {table}")
        
        if table_diff['removed_tables']:
            report.append(f"\n❌ REMOVED TABLES ({len(table_diff['removed_tables'])})")
            for table in sorted(table_diff['removed_tables']):
                report.append(f"  - {table}")
        
        # Column changes in common tables
        modified_tables = []
        for table in sorted(table_diff['common_tables']):
            col_diff = self.compare_table_columns(table)
            
            if (col_diff['added_columns'] or 
                col_diff['removed_columns'] or 
                col_diff['modified_columns']):
                modified_tables.append((table, col_diff))
        
        if modified_tables:
            report.append(f"\n🔄 MODIFIED TABLES ({len(modified_tables)})")
            
            for table, col_diff in modified_tables:
                report.append(f"\n  Table: {table}")
                
                if col_diff['added_columns']:
                    report.append(f"    + Added columns: {', '.join(sorted(col_diff['added_columns']))}")
                
                if col_diff['removed_columns']:
                    report.append(f"    - Removed columns: {', '.join(sorted(col_diff['removed_columns']))}")
                
                if col_diff['modified_columns']:
                    report.append(f"    ⚠ Modified columns:")
                    for col_name, changes in col_diff['modified_columns'].items():
                        report.append(f"      • {col_name}")
                        report.append(f"        Old: {changes['old']}")
                        report.append(f"        New: {changes['new']}")
        
        report.append("\n" + "="*70)
        report.append("END OF REPORT")
        report.append("="*70)
        
        return "\n".join(report)


def main():
    """Command-line interface"""
    if len(sys.argv) < 3:
        print("""
Usage: python schema_diff.py OLD_DB NEW_DB [OPTIONS]

Generate database schema comparison and migration script.

Options:
  -o FILE          Output migration SQL to file
  -r FILE          Output diff report to file
  --drop           Include DROP statements for removed tables
  --print          Print migration SQL to console

Examples:
  # Generate migration script
  python schema_diff.py old.db new.db -o migration.sql
  
  # Generate diff report
  python schema_diff.py old.db new.db -r diff_report.txt
  
  # Both
  python schema_diff.py old.db new.db -o migration.sql -r report.txt --drop
        """)
        sys.exit(1)
    
    old_db = sys.argv[1]
    new_db = sys.argv[2]
    
    # Parse options
    output_file = None
    report_file = None
    include_drops = False
    print_to_console = False
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '-o' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '-r' and i + 1 < len(sys.argv):
            report_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--drop':
            include_drops = True
            i += 1
        elif sys.argv[i] == '--print':
            print_to_console = True
            i += 1
        else:
            i += 1
    
    try:
        print(f"🔍 Comparing databases...")
        print(f"   Old: {old_db}")
        print(f"   New: {new_db}\n")
        
        diff = SchemaDiff(old_db, new_db)
        
        # Generate migration
        if output_file or print_to_console:
            migration_sql = diff.generate_migration_sql(include_drops=include_drops)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(migration_sql)
                print(f"✅ Migration script saved to: {output_file}")
            
            if print_to_console:
                print("\n" + "="*70)
                print("MIGRATION SQL")
                print("="*70)
                print(migration_sql)
        
        # Generate report
        if report_file or (not output_file and not print_to_console):
            report = diff.generate_diff_report()
            
            if report_file:
                with open(report_file, 'w') as f:
                    f.write(report)
                print(f"✅ Diff report saved to: {report_file}")
            else:
                print(report)
        
        print("\n✅ Comparison complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
