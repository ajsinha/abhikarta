```
═══════════════════════════════════════════════════════════════════════════════
Copyright 2025-2030, All rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
═══════════════════════════════════════════════════════════════════════════════
```

# AI Insights - Comprehensive Documentation

**Version:** 2.1 (JSON-Based ID Implementation)  
**Author:** Ashutosh Sinha (ajsinha@gmail.com)  
**Repository:** https://www.github.com/ajsinha/abhikarta  
**Last Updated:** November 5, 2024

---

## Table of Contents

1. [Overview](#overview)
2. [JSON-Based ID Structure](#json-based-id-structure)
3. [Design Architecture](#design-architecture)
4. [Implementation Details](#implementation-details)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Sample Code](#sample-code)
8. [Deployment Guide](#deployment-guide)
9. [Troubleshooting](#troubleshooting)
10. [Migration from v2.0 to v2.1](#migration-guide)

---

## Overview

### What is AI Insights?

AI Insights is a document management and visualization system designed to display and manage markdown-based analytical reports, insights, and documentation within the Abhikarta multi-agent orchestration platform.

### Key Features

- **Filesystem-based storage** - No database required for insights
- **Dual categorization** - Global (all users) and User-specific insights
- **JSON-based IDs** - Explicit category, owner, and document structure
- **Auto-refresh** - Configurable countdown timer with toggle
- **Export to Word** - One-click markdown to DOCX conversion (Pure Python)
- **Automatic cleanup** - Scheduled deletion of old files (configurable retention)
- **Rich UI** - Search, sort, pagination, and markdown rendering
- **Delete capability** - Users can delete their own insights
- **Pure Python** - No Node.js or external dependencies
- **Secure access control** - Owner-based permissions

### Use Cases

1. **AI-Generated Reports** - Store and view outputs from AI workflows
2. **Analysis Documentation** - Centralized location for analytical insights
3. **Knowledge Management** - Share global insights across the organization
4. **Personal Notes** - Users maintain their own private insights
5. **Workflow Outputs** - Automatically generated documentation from DAG executions
6. **Temporary Reports** - Auto-delete old reports after retention period

---

## JSON-Based ID Structure

### Overview

AI Insights uses a JSON-based ID structure for identifying documents. This provides clear separation of concerns and explicit ownership information.

### ID Format

Each insight ID contains three fields:

```json
{
  "category": "Global" | "User",
  "owner": "<userid>" | "admin",
  "document": "<filename>.md"
}
```

### Field Descriptions

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| **category** | string | Type of insight | `"Global"` or `"User"` |
| **owner** | string | Who owns the document | `"admin"`, `"user123"`, etc. |
| **document** | string | Filename with extension | `"Q4_Report.md"`, `"Analysis.md"` |

### Encoding Process

The JSON object is base64-URL-encoded for safe transmission in URLs:

1. **Create JSON object**
2. **Serialize** with minimal separators: `json.dumps(data, separators=(',', ':'))`
3. **Encode** to base64: `base64.urlsafe_b64encode(json_string.encode())`
4. **Decode** to string: `.decode()`

**Example:**
```python
import json
import base64

# Original data
id_data = {
    "category": "Global",
    "owner": "admin",
    "document": "Q4_2024_Market_Trends.md"
}

# Encode
id_json = json.dumps(id_data, separators=(',', ':'))
# Result: '{"category":"Global","owner":"admin","document":"Q4_2024_Market_Trends.md"}'

id_encoded = base64.urlsafe_b64encode(id_json.encode()).decode()
# Result: 'eyJjYXRlZ29yeSI6Ikdsb2JhbCIsIm93bmVyIjoiYWRtaW4iLCJkb2N1bWVudCI6IlE0XzIwMjRfTWFya2V0X1RyZW5kcy5tZCJ9'
```

### ID Examples

#### Example 1: Global Insight

**JSON:**
```json
{
  "category": "Global",
  "owner": "admin",
  "document": "Q4_2024_Market_Trends.md"
}
```

**Encoded ID:**
```
eyJjYXRlZ29yeSI6Ikdsb2JhbCIsIm93bmVyIjoiYWRtaW4iLCJkb2N1bWVudCI6IlE0XzIwMjRfTWFya2V0X1RyZW5kcy5tZCJ9
```

**File Location:**
```
data/ai_insights/all/Q4_2024_Market_Trends.md
```

#### Example 2: User Insight

**JSON:**
```json
{
  "category": "User",
  "owner": "user123",
  "document": "My_Personal_Analysis.md"
}
```

**Encoded ID:**
```
eyJjYXRlZ29yeSI6IlVzZXIiLCJvd25lciI6InVzZXIxMjMiLCJkb2N1bWVudCI6Ik15X1BlcnNvbmFsX0FuYWx5c2lzLm1kIn0
```

**File Location:**
```
data/ai_insights/users/user123/My_Personal_Analysis.md
```

### Parsing IDs

```python
import json
import base64

def parse_insight_id(insight_id):
    """
    Decode and parse a JSON-based insight ID
    
    Returns: (category, owner, document) tuple
    Raises: ValueError if invalid
    """
    try:
        # Decode from base64
        id_json = base64.urlsafe_b64decode(insight_id.encode()).decode()
        
        # Parse JSON
        id_data = json.loads(id_json)
        
        # Extract fields
        category = id_data.get('category')
        owner = id_data.get('owner')
        document = id_data.get('document')
        
        # Validate
        if not all([category, owner, document]):
            raise ValueError("Missing required fields")
        
        if category not in ['Global', 'User']:
            raise ValueError("Invalid category")
        
        return category, owner, document
        
    except Exception as e:
        raise ValueError(f"Invalid insight ID: {e}")
```

### Building File Paths

```python
base_dir = 'data/ai_insights'

if category == 'Global':
    filepath = os.path.join(base_dir, 'all', document)
    
elif category == 'User':
    filepath = os.path.join(base_dir, 'users', owner, document)
```

### Access Control Rules

1. **Global Insights**
   - All authenticated users can READ
   - All authenticated users can EXPORT
   - Only admins can DELETE (future feature)
   - Owner is always `"admin"`

2. **User Insights**
   - Only the owner can READ
   - Only the owner can EXPORT
   - Only the owner can DELETE
   - Owner is the user_id

### Benefits of JSON-Based IDs

✅ **Explicit Ownership** - Owner is clearly defined in the ID  
✅ **Better Security** - Access control built into ID structure  
✅ **Self-Documenting** - ID tells you what it represents  
✅ **Extensible** - Can add more fields without breaking changes  
✅ **Type-Safe** - Category and owner are explicit  
✅ **Audit-Friendly** - Clear ownership trail  

---

## Design Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Web Browser (Client)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Search/Filter│  │ Auto-Refresh │  │  Pagination  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           AI Insights UI (ai_insights.html)          │   │
│  │  ┌────────────────┐  ┌──────────────────────────┐   │   │
│  │  │  Left Panel    │  │    Right Panel           │   │   │
│  │  │  (Table 35%)   │  │    (Viewer 65%)          │   │   │
│  │  │                │  │                          │   │   │
│  │  │  Category      │  │  [Delete] [Export]       │   │   │
│  │  │  Document      │  │                          │   │   │
│  │  │                │  │  Markdown Viewer         │   │   │
│  │  └────────────────┘  └──────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────┬───────────────────────────────────────────┘
                   │ AJAX/REST API (JSON IDs)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  Flask Application Server                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          ViewRoutes (view_routes.py)                 │   │
│  │                                                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ JSON ID    │  │ Export     │  │ Cleanup    │    │   │
│  │  │ Generation │  │ Engine     │  │ Monitor    │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  │                                                       │   │
│  │  API Endpoints:                                      │   │
│  │  - GET  /api/insights        (List with JSON IDs)   │   │
│  │  - GET  /api/insight/<id>    (Read, verify owner)   │   │
│  │  - GET  /api/export-insight  (Export, verify owner) │   │
│  │  - DEL  /api/delete-insight  (Delete, verify owner) │   │
│  │  - POST /api/cleanup-insights (Manual Cleanup)      │   │
│  │  - GET  /api/cleanup-status  (Status)               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │    Markdown Converter (markdown_to_docx.py)          │   │
│  │                  Pure Python                          │   │
│  │  - Parses markdown syntax                            │   │
│  │  - Generates DOCX with python-docx                   │   │
│  │  - Supports: headers, lists, tables, code, quotes    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │      Cleanup Monitor (Background Thread)             │   │
│  │                                                       │   │
│  │  - Runs every N hours (configurable)                 │   │
│  │  - Deletes files older than M days (configurable)    │   │
│  │  - Daemon thread (stops with Flask)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────┬───────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Filesystem Storage                        │
│                                                              │
│  data/ai_insights/                                          │
│  ├── all/                    (Global - Read by all users)  │
│  │   ├── Q4_Report.md                                      │
│  │   ├── Analysis.md                                       │
│  │   └── ...                                               │
│  └── users/                  (User-specific - Private)     │
│      ├── user123/                                           │
│      │   ├── My_Notes.md                                   │
│      │   └── Project_Plan.md                               │
│      ├── user456/                                           │
│      │   └── Personal_Analysis.md                          │
│      └── ...                                                │
└─────────────────────────────────────────────────────────────┘
```

### Access Control Matrix

| Operation | Global Insight | User Insight (Own) | User Insight (Other) |
|-----------|----------------|--------------------|-----------------------|
| **READ** | ✅ Allowed | ✅ Allowed | ❌ Denied (403) |
| **EXPORT** | ✅ Allowed | ✅ Allowed | ❌ Denied (403) |
| **DELETE** | ❌ Denied (403) | ✅ Allowed | ❌ Denied (403) |

---

## Implementation Details

### Backend Implementation (Python/Flask)

#### File: `routes/view_routes.py`

**Class:** `ViewRoutes(BaseRoutes)`

**Key Methods:**
1. **`register_routes()`** - Registers all Flask route handlers
2. **`_cleanup_old_files()`** - Scans and deletes old files
3. **`_start_cleanup_monitor()`** - Creates background thread

**Configuration:**
```python
# Read from environment or use defaults
self.retention_days = int(os.environ.get('AI_INSIGHTS_RETENTION_DAYS', '15'))
self.cleanup_interval_hours = int(os.environ.get('AI_INSIGHTS_CLEANUP_INTERVAL_HOURS', '24'))
```

#### ID Generation Implementation

```python
import json
import base64

# For Global insights
for filename in os.listdir(global_dir):
    if filename.endswith('.md'):
        id_data = {
            'category': 'Global',
            'owner': 'admin',
            'document': filename
        }
        id_json = json.dumps(id_data, separators=(',', ':'))
        id_encoded = base64.urlsafe_b64encode(id_json.encode()).decode()
        
        insights.append({
            'id': id_encoded,
            'category': 'Global',
            'owner': 'admin',
            'document': filename[:-3],
            'filepath': filepath,
            'filename': filename,
            'created_at': created_at
        })
```

#### ID Parsing with Access Control

```python
def parse_insight_id(insight_id, current_user_id):
    """Parse and validate JSON-based insight ID"""
    try:
        id_json = base64.urlsafe_b64decode(insight_id.encode()).decode()
        id_data = json.loads(id_json)
        
        category = id_data.get('category')
        owner = id_data.get('owner')
        document = id_data.get('document')
        
        if not all([category, owner, document]):
            raise ValueError("Missing required fields")
        
        if category not in ['Global', 'User']:
            raise ValueError("Invalid category")
        
        # Verify access for User insights
        if category == 'User' and owner != current_user_id:
            raise PermissionError("Access denied")
        
        # Build filepath
        base_dir = 'data/ai_insights'
        if category == 'Global':
            filepath = os.path.join(base_dir, 'all', document)
        else:
            filepath = os.path.join(base_dir, 'users', owner, document)
        
        return category, owner, document, filepath
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in ID: {e}")
```

### Frontend Implementation (HTML/JavaScript)

#### Key JavaScript Functions:

```javascript
// Fetching insights - IDs are opaque to frontend
function loadInsights() {
    $.get('/api/insights', function(response) {
        if (response.success) {
            response.insights.forEach(function(insight) {
                const row = $('<tr>')
                    .attr('data-insight-id', insight.id)  // Base64 JSON
                    .attr('data-category', insight.category)
                    .attr('data-owner', insight.owner);
                // ... render row
            });
        }
    });
}

// Using JSON ID
function loadInsightContent(insightId, documentName, category, owner) {
    $.get(`/api/insight/${insightId}`, function(response) {
        $('#insightViewer').html(marked.parse(response.content));
        
        // Show/hide delete button based on ownership
        if (category === 'User' && owner === currentUserId) {
            $('#deleteBtn').show();
        } else {
            $('#deleteBtn').hide();
        }
    });
}
```

---

## API Reference

### Base URL

```
http://localhost:5001  (development)
https://yourapp.com    (production)
```

### Authentication

All endpoints require user authentication via Flask session.

---

### 1. Get Insights List

**Endpoint:** `GET /api/insights`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | int | 1 | Page number |
| per_page | int | 10 | Items per page |
| search | string | "" | Search term |
| sort_by | string | "document" | Sort field |
| sort_order | string | "asc" | Sort order |

**Response (200):**
```json
{
  "success": true,
  "insights": [
    {
      "id": "eyJjYXRlZ29yeSI6Ikdsb2JhbCIsIm93bmVyIjoiYWRtaW4iLCJkb2N1bWVudCI6IlE0X1JlcG9ydC5tZCJ9",
      "category": "Global",
      "owner": "admin",
      "document": "Q4_Report",
      "filename": "Q4_Report.md",
      "created_at": "2024-11-01T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

---

### 2. Get Insight Content

**Endpoint:** `GET /api/insight/<path:insight_id>`

**Response Success (200):**
```json
{
  "success": true,
  "content": "# Report\n\nContent here...",
  "category": "Global",
  "owner": "admin",
  "document": "Q4_Report.md"
}
```

**Response Error (403):**
```json
{
  "success": false,
  "content": "# Access Denied\n\nYou do not have permission to view this insight."
}
```

---

### 3. Export Insight to Word

**Endpoint:** `GET /api/export-insight/<path:insight_id>`

**Response Success (200):**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Body: Binary DOCX file

**Response Error (403):**
```json
{
  "success": false,
  "error": "Access denied: You can only export your own insights"
}
```

---

### 4. Delete Insight

**Endpoint:** `DELETE /api/delete-insight/<path:insight_id>`

**Response Success (200):**
```json
{
  "success": true,
  "message": "Insight deleted successfully"
}
```

**Response Error (403):**
```json
{
  "success": false,
  "error": "Only user insights can be deleted"
}
```

---

### 5. Manual Cleanup

**Endpoint:** `POST /api/cleanup-insights`

**Response (200):**
```json
{
  "success": true,
  "message": "Cleanup completed: 5 file(s) deleted",
  "deleted_count": 5,
  "retention_days": 15
}
```

---

### 6. Get Cleanup Status

**Endpoint:** `GET /api/cleanup-status`

**Response (200):**
```json
{
  "success": true,
  "retention_days": 15,
  "cleanup_interval_hours": 24,
  "total_insights": 42,
  "old_insights": 3
}
```

---

## Configuration

### Environment Variables

```bash
# Retention period (days) - Default: 15
export AI_INSIGHTS_RETENTION_DAYS=15

# Cleanup interval (hours) - Default: 24
export AI_INSIGHTS_CLEANUP_INTERVAL_HOURS=24
```

### Directory Structure

```
data/ai_insights/
├── all/        # Global insights
└── users/      # User insights
```

---

## Sample Code

### Creating an Insight

```python
import os
import json
import base64

def create_insight(user_id, title, content, category='user'):
    """Create a new insight with JSON-based ID"""
    safe_title = title.replace(' ', '_')
    filename = f"{safe_title}.md"
    
    if category.lower() == 'global':
        directory = 'data/ai_insights/all'
        owner = 'admin'
        cat = 'Global'
    else:
        directory = f'data/ai_insights/users/{user_id}'
        owner = user_id
        cat = 'User'
    
    os.makedirs(directory, exist_ok=True)
    
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Create JSON ID
    id_data = {'category': cat, 'owner': owner, 'document': filename}
    id_json = json.dumps(id_data, separators=(',', ':'))
    id_encoded = base64.urlsafe_b64encode(id_json.encode()).decode()
    
    return id_encoded
```

### Parsing an ID

```python
import json
import base64

def parse_insight_id(insight_id):
    """Parse JSON-based insight ID"""
    id_json = base64.urlsafe_b64decode(insight_id.encode()).decode()
    return json.loads(id_json)
```

### Fetching Insights via API

```python
import requests

response = requests.get(
    'http://localhost:5001/api/insights',
    cookies={'session': session_cookie}
)

if response.status_code == 200:
    insights = response.json()['insights']
    for insight in insights:
        print(f"{insight['category']}: {insight['document']}")
```

### Exporting to Word

```python
import requests

insight_id = "eyJjYXRlZ29yeSI6Ikdsb2JhbCIsIm93bmVyIjoiYWRtaW4iLCJkb2N1bWVudCI6IlJlcG9ydC5tZCJ9"

response = requests.get(
    f'http://localhost:5001/api/export-insight/{insight_id}',
    cookies={'session': session_cookie}
)

if response.status_code == 200:
    with open('Report.docx', 'wb') as f:
        f.write(response.content)
```

### DAG Integration

```python
import os
import json
import base64
from datetime import datetime

def save_dag_output(dag_id, workflow_id, output_data, user_id):
    """Save DAG execution as insight"""
    markdown = f"""# DAG Execution Report

**DAG ID:** {dag_id}
**Workflow ID:** {workflow_id}
**Executed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Results

"""
    for key, value in output_data.items():
        markdown += f"### {key}\n{value}\n\n"
    
    filename = f"DAG_{dag_id}_{workflow_id}.md"
    directory = f'data/ai_insights/users/{user_id}'
    os.makedirs(directory, exist_ok=True)
    
    with open(os.path.join(directory, filename), 'w') as f:
        f.write(markdown)
    
    # Create JSON ID
    id_data = {'category': 'User', 'owner': user_id, 'document': filename}
    id_json = json.dumps(id_data, separators=(',', ':'))
    return base64.urlsafe_b64encode(id_json.encode()).decode()
```

---

## Deployment Guide

### Prerequisites

```bash
# Python 3.7+
python --version

# Install dependencies
pip install Flask python-docx markdown
```

### Installation

```bash
# Create directories
mkdir -p routes templates utils data/ai_insights/all data/ai_insights/users

# Copy files
cp view_routes.py routes/
cp markdown_to_docx.py utils/
cp ai_insights.html templates/
cp base.html templates/

# Configure
export AI_INSIGHTS_RETENTION_DAYS=15
export AI_INSIGHTS_CLEANUP_INTERVAL_HOURS=24

# Start application
python app.py
```

### Production Deployment

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data/ai_insights/all data/ai_insights/users
ENV AI_INSIGHTS_RETENTION_DAYS=15
ENV AI_INSIGHTS_CLEANUP_INTERVAL_HOURS=24
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

---

## Troubleshooting

### No Insights Showing

```bash
# Check directories exist
ls -la data/ai_insights/all
ls -la data/ai_insights/users

# Add test file
echo "# Test" > data/ai_insights/all/Test.md
```

### Export Not Working

```bash
# Check packages
python -c "import docx; import markdown; print('OK')"

# Install if missing
pip install python-docx markdown
```

### Cleanup Not Running

```bash
# Check logs
grep "Cleanup" /var/log/flask/app.log

# Manually trigger
curl -X POST http://localhost:5001/api/cleanup-insights
```

### Invalid ID Format

```python
# Test ID parsing
import json, base64
try:
    id_json = base64.urlsafe_b64decode(id_string.encode()).decode()
    print(json.loads(id_json))
except Exception as e:
    print(f"Invalid: {e}")
```

---

## Migration from v2.0 to v2.1

### What Changed

**v2.0:** Simple string IDs like `"global_Report.md"`  
**v2.1:** JSON-based IDs: `{"category":"Global","owner":"admin","document":"Report.md"}`

### Migration Steps

1. **Update view_routes.py** with JSON ID implementation
2. **No filesystem changes** - files remain the same
3. **Frontend compatible** - IDs are opaque to JavaScript
4. **Test thoroughly** - verify all API endpoints

### Verification

```bash
# Get insights
curl http://localhost:5001/api/insights

# Test an ID
ID="eyJjYXRlZ29yeSI6Ikdsb2JhbCIsIm93bmVyIjoiYWRtaW4iLCJkb2N1bWVudCI6IlRlc3QubWQifQ"
curl http://localhost:5001/api/insight/$ID
```

### Backward Compatibility

- ❌ Old IDs won't work - must use new JSON format
- ✅ Files unchanged - existing .md files work as-is
- ✅ Frontend works - no JavaScript changes needed

---

## Appendix

### Performance

- Page Load: < 500ms
- Insight List: 10-50ms (100 files)
- Export: 200-500ms (typical document)

### Browser Support

- ✅ Chrome/Edge/Firefox/Safari
- ❌ IE11 not supported

### File Limits

- Markdown files: Recommend < 1MB
- Total insights: No hard limit

### Support

- Email: ajsinha@gmail.com
- GitHub: https://www.github.com/ajsinha/abhikarta

---

**End of Documentation**

Version 2.1 | Last Updated: November 5, 2024

---

```
═══════════════════════════════════════════════════════════════════════════════
Copyright 2025-2030, All rights reserved, Ashutosh Sinha, Email: ajsinha@gmail.com
═══════════════════════════════════════════════════════════════════════════════
```