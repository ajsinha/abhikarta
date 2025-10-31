# Database Schema Tools - Quick Reference

## 📦 All Tools Summary

| Tool | Size | Purpose | Best For |
|------|------|---------|----------|
| **db_schema_extractor.py** | 16K | Full-featured CLI | Power users, automation |
| **schema_extractor_simple.py** | 11K | Simple library | Python scripts, quick tasks |
| **extract_my_schema.py** | 9.8K | Ready-to-use script | Beginners, one-off extracts |
| **schema_diff.py** | 19K | Compare & migrate | Version upgrades, migrations |

## 🚀 Quick Start Commands

### Extract Schema (Easiest)
```bash
# Edit and run
python extract_my_schema.py
```

### Extract Schema (CLI)
```bash
# Basic
python db_schema_extractor.py mydb.sqlite -o schema.sql

# With DROP statements
python db_schema_extractor.py mydb.sqlite -o schema.sql --drop

# Print to console
python db_schema_extractor.py mydb.sqlite --print
```

### Extract Schema (Python)
```python
from schema_extractor_simple import extract_sqlite_schema

schema = extract_sqlite_schema('mydb.sqlite', include_drop=True)
with open('schema.sql', 'w') as f:
    f.write(schema)
```

### Compare Schemas
```bash
# Generate migration
python schema_diff.py old.db new.db -o migration.sql

# Generate diff report
python schema_diff.py old.db new.db -r diff_report.txt

# Both
python schema_diff.py old.db new.db -o migration.sql -r report.txt
```

## 📋 Common Tasks

### Task 1: Backup Current Schema
```bash
python db_schema_extractor.py production.db -o backup_$(date +%Y%m%d).sql --drop
```

### Task 2: Document Database Structure
```bash
python db_schema_extractor.py mydb.sqlite --doc database_docs.txt
```

### Task 3: Clone Database Structure
```python
from schema_extractor_simple import extract_sqlite_schema
import sqlite3

# Extract
schema = extract_sqlite_schema('source.db')

# Apply to new DB
conn = sqlite3.connect('clone.db')
conn.executescript(schema)
conn.close()
```

### Task 4: Compare Two Versions
```bash
python schema_diff.py v1.0.db v2.0.db -r differences.txt
```

### Task 5: Generate Migration
```bash
python schema_diff.py old.db new.db -o upgrade.sql --drop
```

### Task 6: List All Tables
```python
from schema_extractor_simple import list_tables

tables = list_tables('mydb.sqlite')
print(f"Found {len(tables)} tables: {', '.join(tables)}")
```

### Task 7: Get Table Info
```python
from schema_extractor_simple import get_table_columns

columns = get_table_columns('mydb.sqlite', 'users')
for col in columns:
    print(f"{col['name']}: {col['type']}")
```

### Task 8: Extract Single Table
```python
from schema_extractor_simple import extract_table_schema

table_sql = extract_table_schema('mydb.sqlite', 'users')
print(table_sql)
```

## 🎯 Which Tool Should I Use?

### Use `extract_my_schema.py` if you want:
- ✅ Quick, one-time extraction
- ✅ Verbose progress output
- ✅ No command-line arguments
- ✅ Beginner-friendly

### Use `db_schema_extractor.py` if you want:
- ✅ Maximum flexibility
- ✅ Command-line automation
- ✅ Selective extraction (no indexes, no triggers, etc.)
- ✅ Multiple output formats

### Use `schema_extractor_simple.py` if you want:
- ✅ Import as library
- ✅ Use in your own scripts
- ✅ Simple API
- ✅ Quick integration

### Use `schema_diff.py` if you want:
- ✅ Compare two databases
- ✅ Generate migration scripts
- ✅ Track schema changes
- ✅ Upgrade/downgrade paths

## 📝 Output Examples

### Standard Schema Output
```sql
-- ============================================
-- Database Schema Export
-- ============================================

-- Table: users
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    created_at TEXT
);

CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Table: workflows
DROP TABLE IF EXISTS workflows;
CREATE TABLE workflows (
    workflow_id TEXT PRIMARY KEY,
    user_id TEXT,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Diff Report Output
```
======================================================================
DATABASE SCHEMA COMPARISON REPORT
======================================================================
Old Database: v1.0.db
New Database: v2.0.db

📊 TABLES
  Total in old: 10
  Total in new: 12
  Added: 2
  Removed: 0
  Common: 10

✅ ADDED TABLES (2)
  + notifications
  + audit_log

🔄 MODIFIED TABLES (3)
  Table: users
    + Added columns: last_login, updated_at
    ⚠ Modified columns:
      • email
        Old: {'type': 'TEXT', 'notnull': False}
        New: {'type': 'TEXT', 'notnull': True}
```

### Migration Script Output
```sql
-- ============================================
-- Database Migration Script
-- ============================================

-- NEW TABLES
CREATE TABLE notifications (
    notification_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    message TEXT,
    created_at TEXT
);

-- MODIFIED TABLES
ALTER TABLE users ADD COLUMN last_login TEXT;
ALTER TABLE users ADD COLUMN updated_at TEXT;

-- WARNING: Column modification requires table recreation
-- See detailed steps below...
```

## 💡 Pro Tips

1. **Always backup first!**
   ```bash
   cp production.db production_backup_$(date +%Y%m%d).db
   ```

2. **Test migrations in development**
   ```bash
   cp production.db test.db
   sqlite3 test.db < migration.sql
   ```

3. **Track schema in version control**
   ```bash
   python db_schema_extractor.py db.sqlite -o schema.sql --no-comments
   git add schema.sql
   git commit -m "Update schema"
   ```

4. **Generate documentation regularly**
   ```bash
   python db_schema_extractor.py db.sqlite --doc docs/schema.txt
   ```

5. **Compare before deploying**
   ```bash
   python schema_diff.py dev.db prod.db -r pre_deploy_diff.txt
   ```

## 🔧 Advanced Usage

### Chain Multiple Operations
```bash
# Extract, compare, and document
python db_schema_extractor.py old.db -o old_schema.sql
python db_schema_extractor.py new.db -o new_schema.sql
python schema_diff.py old.db new.db -o migration.sql -r changes.txt
python db_schema_extractor.py new.db --doc final_docs.txt
```

### Python Script Integration
```python
from schema_extractor_simple import (
    extract_sqlite_schema,
    list_tables,
    get_table_columns,
    compare_schemas
)

# Get all info
schema = extract_sqlite_schema('mydb.sqlite')
tables = list_tables('mydb.sqlite')

# Process each table
for table in tables:
    columns = get_table_columns('mydb.sqlite', table)
    print(f"{table}: {len(columns)} columns")

# Compare with another DB
diff = compare_schemas('old.db', 'new.db')
if diff['only_in_db2']:
    print(f"New tables: {diff['only_in_db2']}")
```

### Automated Backup Script
```python
#!/usr/bin/env python3
from datetime import datetime
from schema_extractor_simple import export_schema_to_file

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f"backups/schema_{timestamp}.sql"

export_schema_to_file('production.db', output_file, include_drop=True)
print(f"Backup saved: {output_file}")
```

## 📚 Function Reference

### schema_extractor_simple.py

| Function | Returns | Description |
|----------|---------|-------------|
| `extract_sqlite_schema(db, drop)` | str | Full schema SQL |
| `extract_table_schema(db, table)` | str | Single table SQL |
| `get_table_columns(db, table)` | list | Column information |
| `list_tables(db)` | list | All table names |
| `export_schema_to_file(db, file, drop)` | None | Export to file |
| `compare_schemas(db1, db2)` | dict | Schema differences |

### db_schema_extractor.py (Class-based)

| Method | Description |
|--------|-------------|
| `connect()` | Connect to database |
| `get_tables()` | Get all table names |
| `get_table_schema(table)` | Get CREATE TABLE SQL |
| `get_indexes(table)` | Get all indexes |
| `get_triggers(table)` | Get all triggers |
| `generate_schema_sql(**opts)` | Generate complete schema |
| `export_to_file(file, **opts)` | Export to file |

### schema_diff.py (Class-based)

| Method | Description |
|--------|-------------|
| `compare_tables()` | Compare table structures |
| `compare_table_columns(table)` | Compare columns |
| `generate_migration_sql(**opts)` | Generate migration |
| `generate_diff_report()` | Generate report |

## 🆘 Troubleshooting

### Error: Database is locked
```python
# Close all connections
import sqlite3
for conn in sqlite3.connections:
    conn.close()
```

### Error: Permission denied
```bash
chmod 644 mydb.sqlite
```

### Error: No module named 'schema_extractor_simple'
```bash
# Make sure file is in same directory or add to path
export PYTHONPATH="${PYTHONPATH}:/path/to/scripts"
```

### Warning: SQLite doesn't support ALTER COLUMN
This is normal. SQLite has limited ALTER TABLE support. Use the table recreation method provided in migration scripts.

## 📞 Support

For issues or questions:
1. Check the comprehensive README: `SCHEMA_EXTRACTOR_README.md`
2. Review usage examples in `schema_extractor_simple.py`
3. Test with `extract_my_schema.py` first

## ✅ Checklist for Safe Schema Changes

- [ ] Backup database before any changes
- [ ] Extract current schema for reference
- [ ] Compare old and new schemas
- [ ] Review migration script carefully
- [ ] Test migration on copy of database
- [ ] Verify data integrity after migration
- [ ] Update documentation
- [ ] Commit schema to version control

---

**Remember:** Always test schema changes in a development environment first!
