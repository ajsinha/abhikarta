# Database Schema Extractor Tools

Three Python scripts to extract database schemas and generate executable SQL DDL statements.

## 📦 Files Included

1. **`db_schema_extractor.py`** - Full-featured command-line tool with many options
2. **`schema_extractor_simple.py`** - Simple library with usage examples
3. **`extract_my_schema.py`** - Ready-to-use practical script

## 🚀 Quick Start

### Option 1: Use the Ready-Made Script (Easiest)

```bash
# Edit the script to set your database path
nano extract_my_schema.py  # Change DATABASE_PATH variable

# Run it
python extract_my_schema.py
```

This will:
- Show a summary of all tables
- Extract complete schema with DROP statements
- Save to `schema_export.sql`

### Option 2: Use the Simple Library

```python
from schema_extractor_simple import extract_sqlite_schema

# Extract schema
schema = extract_sqlite_schema('mydb.sqlite', include_drop=True)

# Save to file
with open('schema.sql', 'w') as f:
    f.write(schema)
```

### Option 3: Use the Advanced CLI Tool

```bash
# Basic extraction
python db_schema_extractor.py mydb.sqlite -o schema.sql

# With DROP statements
python db_schema_extractor.py mydb.sqlite -o schema.sql --drop

# Print to console
python db_schema_extractor.py mydb.sqlite --print

# Generate documentation
python db_schema_extractor.py mydb.sqlite --doc schema_docs.txt
```

## 📋 Detailed Documentation

### 1. Full-Featured CLI Tool (`db_schema_extractor.py`)

#### Features
- ✅ Extract complete database schema
- ✅ Support for tables, indexes, triggers, and views
- ✅ Optional DROP statements
- ✅ Generate human-readable documentation
- ✅ Print to console or save to file
- ✅ Extensible for multiple database types

#### Command-Line Usage

```bash
# Basic usage
python db_schema_extractor.py DATABASE_FILE -o OUTPUT_FILE

# All options
python db_schema_extractor.py DATABASE_FILE [OPTIONS]

Options:
  -o, --output FILE        Output SQL file path
  -t, --type TYPE          Database type (sqlite, postgresql, mysql, mssql)
  --drop                   Include DROP TABLE statements
  --no-indexes             Exclude indexes from output
  --no-triggers            Exclude triggers from output
  --no-views               Exclude views from output
  --no-comments            Exclude SQL comments from output
  --doc FILE               Export documentation to text file
  --print                  Print schema to console
```

#### Examples

```bash
# Extract entire schema
python db_schema_extractor.py mydb.sqlite -o schema.sql

# Extract with DROP statements for clean recreation
python db_schema_extractor.py mydb.sqlite -o schema.sql --drop

# Extract without indexes and triggers
python db_schema_extractor.py mydb.sqlite -o schema.sql --no-indexes --no-triggers

# Generate documentation file
python db_schema_extractor.py mydb.sqlite --doc database_docs.txt

# Print to console for quick inspection
python db_schema_extractor.py mydb.sqlite --print

# Minimal output (no comments)
python db_schema_extractor.py mydb.sqlite -o minimal.sql --no-comments

# Extract everything
python db_schema_extractor.py mydb.sqlite -o complete.sql --drop --doc docs.txt
```

### 2. Simple Library (`schema_extractor_simple.py`)

#### Functions

##### `extract_sqlite_schema(db_path, include_drop=False)`
Extract complete database schema as SQL string.

```python
schema = extract_sqlite_schema('mydb.sqlite', include_drop=True)
with open('schema.sql', 'w') as f:
    f.write(schema)
```

##### `extract_table_schema(db_path, table_name)`
Extract schema for a single table.

```python
users_table = extract_table_schema('mydb.sqlite', 'users')
print(users_table)
```

##### `get_table_columns(db_path, table_name)`
Get detailed column information.

```python
columns = get_table_columns('mydb.sqlite', 'users')
for col in columns:
    print(f"{col['name']}: {col['type']}")
```

##### `list_tables(db_path)`
List all tables in database.

```python
tables = list_tables('mydb.sqlite')
print(f"Found {len(tables)} tables: {', '.join(tables)}")
```

##### `export_schema_to_file(db_path, output_file, include_drop=False)`
Export schema directly to file.

```python
export_schema_to_file('mydb.sqlite', 'schema.sql', include_drop=True)
```

##### `compare_schemas(db1_path, db2_path)`
Compare schemas of two databases.

```python
diff = compare_schemas('old.sqlite', 'new.sqlite')
print(f"New tables: {diff['only_in_db2']}")
print(f"Removed tables: {diff['only_in_db1']}")
```

#### Usage Examples in the File

The file includes 9 complete examples:
1. Basic schema extraction
2. With DROP statements
3. Single table extraction
4. Table column information
5. List all tables
6. Export helper function
7. Compare databases
8. Recreate database from schema
9. Generate migration script

### 3. Practical Script (`extract_my_schema.py`)

#### Features
- ✅ Pre-configured for immediate use
- ✅ Verbose output with progress tracking
- ✅ Table summary before extraction
- ✅ Detailed statistics
- ✅ Error handling
- ✅ File size reporting

#### Usage

1. **Edit the configuration:**
   ```python
   DATABASE_PATH = "mydb.sqlite"        # Your database file
   OUTPUT_SQL_FILE = "schema_export.sql" # Output file
   INCLUDE_DROP_STATEMENTS = True        # Include DROP statements
   ```

2. **Run the script:**
   ```bash
   python extract_my_schema.py
   ```

3. **Output:**
   - Console: Progress and statistics
   - File: Complete SQL schema

#### Output Example

```
╔════════════════════════════════════════════════════════════════════╗
║                  DATABASE SCHEMA EXTRACTOR                         ║
╚════════════════════════════════════════════════════════════════════╝

======================================================================
DATABASE TABLE SUMMARY: mydb.sqlite
======================================================================

Table Name                     Columns    Has Indexes  Has Triggers
----------------------------------------------------------------------
users                          8          True         False
workflows                      10         True         True
agents                         7          True         False
...

Total Tables: 12

======================================================================

🚀 Starting schema extraction...

======================================================================
DATABASE SCHEMA EXTRACTION
======================================================================
Source Database: mydb.sqlite
Output File: schema_export.sql
Include DROP statements: True
======================================================================

📋 Found 12 tables:
    1. users
    2. workflows
    3. agents
    ...

⚙️  Processing table 1/12: users
   └─ 8 columns
   └─ 2 indexes

⚙️  Processing table 2/12: workflows
   └─ 10 columns
   └─ 3 indexes
   └─ 1 triggers

...

======================================================================
✅ SUCCESS!
======================================================================
Schema exported to: schema_export.sql
File size: 45,231 bytes
Total tables: 12
Total views: 2

💡 You can now run this SQL file on any SQLite database to recreate the schema.
======================================================================
```

## 📝 Generated SQL Output

The generated SQL file will contain:

```sql
-- ============================================
-- Database Schema Export
-- ============================================
-- Source: mydb.sqlite
-- Generated: 2025-10-31 12:34:56
-- ============================================


-- ============================================
-- Table: users
-- ============================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT,
    email TEXT,
    role TEXT DEFAULT 'user',
    last_login TEXT,
    created_at TEXT,
    updated_at TEXT
);

-- Columns: user_id, username, full_name, email, role, last_login, created_at, updated_at

-- Indexes for users:
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);


-- ============================================
-- Table: workflows
-- ============================================
DROP TABLE IF EXISTS workflows;
CREATE TABLE workflows (
    workflow_id TEXT PRIMARY KEY,
    dag_id TEXT NOT NULL,
    name TEXT,
    status TEXT DEFAULT 'pending',
    created_by TEXT,
    created_at TEXT,
    started_at TEXT,
    completed_at TEXT,
    error_message TEXT,
    results TEXT,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- And so on...
```

## 🎯 Use Cases

### 1. Backup Schema
```bash
# Backup current schema
python db_schema_extractor.py production.db -o backup_schema_$(date +%Y%m%d).sql --drop
```

### 2. Migrate Between Environments
```python
# Extract from development
schema = extract_sqlite_schema('dev.db', include_drop=True)

# Apply to production
import sqlite3
conn = sqlite3.connect('prod.db')
conn.executescript(schema)
conn.close()
```

### 3. Documentation Generation
```bash
# Generate comprehensive documentation
python db_schema_extractor.py mydb.sqlite --doc database_structure.txt
```

### 4. Version Control
```bash
# Add schema to git for tracking
python db_schema_extractor.py mydb.sqlite -o schema.sql --no-comments
git add schema.sql
git commit -m "Update database schema"
```

### 5. Compare Versions
```python
from schema_extractor_simple import compare_schemas

diff = compare_schemas('v1.0.db', 'v2.0.db')

print("New tables in v2.0:")
for table in diff['only_in_db2']:
    print(f"  - {table}")

print("\nRemoved tables:")
for table in diff['only_in_db1']:
    print(f"  - {table}")
```

### 6. Clone Database Structure
```python
# Clone structure without data
from schema_extractor_simple import extract_sqlite_schema
import sqlite3

# Extract schema
schema = extract_sqlite_schema('source.db', include_drop=False)

# Create new database with same structure
conn = sqlite3.connect('clone.db')
conn.executescript(schema)
conn.close()
```

## ⚙️ Advanced Usage

### Extract Class-Based API

```python
from db_schema_extractor import DatabaseSchemaExtractor

# Initialize
extractor = DatabaseSchemaExtractor('mydb.sqlite', 'sqlite')
extractor.connect()

# Get tables
tables = extractor.get_tables()
print(f"Tables: {tables}")

# Get detailed info for a table
table_info = extractor.get_table_info('users')
for col in table_info:
    print(f"{col['name']}: {col['type']}")

# Get foreign keys
fks = extractor.get_foreign_keys('workflows')
for fk in fks:
    print(f"{fk['from']} -> {fk['table']}.{fk['to']}")

# Generate schema with options
schema = extractor.generate_schema_sql(
    include_drop=True,
    include_indexes=True,
    include_triggers=True,
    include_views=True,
    include_comments=True
)

# Export
extractor.export_to_file('complete_schema.sql')
extractor.export_documentation('schema_docs.txt')

# Cleanup
extractor.disconnect()
```

### Custom SQL Generation

```python
import sqlite3

def generate_custom_schema(db_path, tables_to_include):
    """Generate schema for specific tables only"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    sql_parts = []
    
    for table in tables_to_include:
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table,))
        
        result = cursor.fetchone()
        if result:
            sql_parts.append(f"{result[0]};")
    
    conn.close()
    return "\n\n".join(sql_parts)

# Use it
schema = generate_custom_schema('mydb.sqlite', ['users', 'workflows'])
print(schema)
```

## 🔧 Requirements

- Python 3.6+
- sqlite3 (built-in)
- No external dependencies!

## 📄 License

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com

## 🤝 Contributing

Feel free to extend these tools for:
- PostgreSQL support
- MySQL support
- SQL Server support
- Data export along with schema
- Schema diff generation
- Migration script generation

## 💡 Tips

1. **Always test on a copy first** - Especially when using DROP statements
2. **Use version control** - Track schema changes in git
3. **Document changes** - Use the documentation generator
4. **Backup regularly** - Schema + data
5. **Compare before migrate** - Use compare_schemas() function

## 🐛 Troubleshooting

### Database is locked
```python
# Close all connections first
import sqlite3
conn = sqlite3.connect('mydb.sqlite')
conn.close()
```

### Permission denied
```bash
# Check file permissions
ls -la mydb.sqlite

# Make readable
chmod 644 mydb.sqlite
```

### Output file exists
```bash
# Remove old file first
rm schema.sql

# Or use -f to force
python db_schema_extractor.py mydb.sqlite -o schema.sql -f
```

## 📚 Additional Resources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQL Best Practices](https://www.sqlstyle.guide/)
- [Database Design Patterns](https://www.databaseanswers.org/data_models/)
