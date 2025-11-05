# Power BI Export Tool - Quick Reference

**Copyright 2025-2030 all rights reserved | Author: Ashutosh Sinha | Email: ajsinha@gmail.com**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials - EASY WAY (Interactive)
python setup_config.py

# Or copy manually
cp config_example.py config.py
# Edit config.py with your credentials

# 3. Run export
python run_export.py
```

---

## 📝 Configuration Cheat Sheet

```python
# config.py

# Authentication (Required)
CLIENT_ID = "your-app-id"
CLIENT_SECRET = "your-secret"
TENANT_ID = "your-tenant-id"

# Report Details (Required)
WORKSPACE_ID = None  # or "workspace-id"
REPORT_ID = "report-id"

# Export Format (Required)
EXPORT_FORMAT = "both"  # "csv" | "pdf" | "both"

# Output Files
CSV_OUTPUT_FILE = "output.csv"
PDF_OUTPUT_FILE = "output.pdf"

# Page Selection (Optional)
PAGE_NAME = None        # CSV: single page or None
PAGE_NAMES = None       # PDF: ["Page1", "Page2"] or None
```

---

## 🔑 Finding Report IDs

**Method 1: From URL**
```
https://app.powerbi.com/groups/{workspace-id}/reports/{report-id}/...
                                  └─────────┘        └─────────┘
```

**Method 2: Use the script**
```python
from powerbi_export import PowerBIExporter

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()
exporter.list_workspaces()  # Shows workspace IDs
exporter.list_reports(WORKSPACE_ID)  # Shows report IDs
```

---

## 💻 Code Examples

### Export to CSV Only
```python
from powerbi_export import PowerBIExporter

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

exporter.export_report_to_csv(
    report_id="abc123",
    output_file="data.csv",
    workspace_id="xyz789",
    page_name="DataPage"  # Optional
)
```

### Export to PDF Only
```python
exporter.export_report_to_pdf(
    report_id="abc123",
    output_file="report.pdf",
    workspace_id="xyz789",
    page_names=["Summary", "Charts"]  # Optional
)
```

### Export to Both Formats
```python
# Export data
exporter.export_report_to_csv(
    report_id="abc123",
    output_file="data.csv",
    workspace_id="xyz789"
)

# Export presentation
exporter.export_report_to_pdf(
    report_id="abc123",
    output_file="presentation.pdf",
    workspace_id="xyz789"
)
```

---

## 🛠️ Common Tasks

### List All Available Reports
```python
exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()
workspaces = exporter.list_workspaces()
for ws in workspaces:
    print(f"\nWorkspace: {ws['name']}")
    exporter.list_reports(ws['id'])
```

### Get Report Pages
```python
pages = exporter.get_report_pages(REPORT_ID, WORKSPACE_ID)
for page in pages:
    print(f"{page['name']}: {page['displayName']}")
```

### Export with Date-Stamped Filename
```python
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
filename = f"report_{today}.pdf"

exporter.export_report_to_pdf(
    report_id=REPORT_ID,
    output_file=filename,
    workspace_id=WORKSPACE_ID
)
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Authentication Failed** | Verify CLIENT_ID, CLIENT_SECRET, TENANT_ID |
| **Report Not Found** | Check REPORT_ID and workspace access |
| **Export Timeout** | Increase `max_attempts` in the method |
| **Service Principal Error** | Enable in Power BI tenant settings |
| **Permission Denied** | Add service principal to workspace |

---

## 📊 Export Format Quick Comparison

| Format | Speed | Size | Best For |
|--------|-------|------|----------|
| **CSV** | ⚡ Fast | 📦 Small | Data analysis |
| **PDF** | 🐌 Slower | 📚 Larger | Presentations |

**CSV**: Choose for data processing, Excel, databases  
**PDF**: Choose for sharing, printing, archiving

---

## 🔐 Security Checklist

- [ ] Don't commit `config.py` to git
- [ ] Use environment variables in production
- [ ] Rotate client secrets regularly
- [ ] Limit service principal permissions
- [ ] Enable MFA on admin accounts
- [ ] Monitor API usage and logs

---

## 🆘 Getting Help

**Error Messages:**
- Check the console output for detailed error information
- Verify all IDs are correct (workspace, report)
- Ensure service principal has proper permissions

**API Limits:**
- Rate limits apply (check Microsoft docs)
- Large reports may timeout (adjust max_attempts)
- Schedule heavy exports during off-peak hours

**Contact:**
- Email: ajsinha@gmail.com
- Subject: "Power BI Export Tool - [Your Issue]"

---

## 📚 Documentation Files

- **README.md** - Complete setup guide
- **USAGE_EXAMPLES.md** - Detailed examples and use cases
- **CHANGELOG.md** - Version history
- **LICENSE** - Copyright and license information

---

## 🎯 One-Liners

```bash
# Install
pip install requests msal pandas

# Quick test
python -c "from powerbi_export import PowerBIExporter; print('✓ Import successful')"

# Check version
python -c "import msal; print(f'MSAL version: {msal.__version__}')"

# List environment
pip list | grep -E "requests|msal|pandas"
```

---

**Power BI Export Tool v2.0.0**  
*Copyright 2025-2030 Ashutosh Sinha*
