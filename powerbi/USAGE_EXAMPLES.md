# Power BI Export - Usage Examples

**Copyright 2025-2030 all rights reserved**  
**Author:** Ashutosh Sinha  
**Email:** ajsinha@gmail.com

---

This guide provides practical examples for different Power BI export scenarios.

## Table of Contents
- [Quick Start Examples](#quick-start-examples)
- [CSV Export Examples](#csv-export-examples)
- [PDF Export Examples](#pdf-export-examples)
- [Advanced Scenarios](#advanced-scenarios)
- [Common Use Cases](#common-use-cases)

## Quick Start Examples

### Example 1: Export Everything to Both Formats

The simplest way to get started:

```python
# config.py
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-secret"
TENANT_ID = "your-tenant-id"

WORKSPACE_ID = None  # Use 'My Workspace'
REPORT_ID = "your-report-id"

EXPORT_FORMAT = "both"
CSV_OUTPUT_FILE = "report.csv"
PDF_OUTPUT_FILE = "report.pdf"
PAGE_NAME = None
PAGE_NAMES = None
```

Run: `python run_export.py`

This exports the entire report to both CSV and PDF formats.

---

## CSV Export Examples

### Example 2: Export Single Page to CSV for Data Analysis

Perfect for extracting tabular data:

```python
# config.py
EXPORT_FORMAT = "csv"
CSV_OUTPUT_FILE = "sales_data.csv"
PAGE_NAME = "Sales Dashboard"  # Only export this page
```

**Use case:** Extract sales data for Excel analysis

### Example 3: Export All Pages to CSV (Multi-file approach)

For multiple pages, use the class directly:

```python
from powerbi_export import PowerBIExporter

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

# Get all pages
pages = exporter.get_report_pages(REPORT_ID, WORKSPACE_ID)

# Export each page to separate CSV
for page in pages:
    output_file = f"export_{page['name']}.csv"
    exporter.export_report_to_csv(
        report_id=REPORT_ID,
        output_file=output_file,
        workspace_id=WORKSPACE_ID,
        page_name=page['name']
    )
    print(f"Exported {page['name']} to {output_file}")
```

**Use case:** Create separate data files for each report section

---

## PDF Export Examples

### Example 4: Export Entire Report to PDF

For complete report archiving:

```python
# config.py
EXPORT_FORMAT = "pdf"
PDF_OUTPUT_FILE = "Q4_2024_Full_Report.pdf"
PAGE_NAMES = None  # All pages
```

**Use case:** Quarterly report for executive review

### Example 5: Export Specific Pages to PDF

For custom presentations:

```python
# config.py
EXPORT_FORMAT = "pdf"
PDF_OUTPUT_FILE = "Executive_Summary.pdf"
PAGE_NAMES = [
    "Cover Page",
    "Executive Summary",
    "Key Metrics",
    "Recommendations"
]
```

**Use case:** Create executive summary without technical details

### Example 6: Export Different Page Combinations

Create multiple PDF versions:

```python
from powerbi_export import PowerBIExporter

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

# Executive version
exporter.export_report_to_pdf(
    report_id=REPORT_ID,
    output_file="executive_version.pdf",
    workspace_id=WORKSPACE_ID,
    page_names=["Summary", "Key Findings", "Recommendations"]
)

# Technical version
exporter.export_report_to_pdf(
    report_id=REPORT_ID,
    output_file="technical_version.pdf",
    workspace_id=WORKSPACE_ID,
    page_names=["Methodology", "Detailed Analysis", "Data Tables", "Appendix"]
)

# Complete version
exporter.export_report_to_pdf(
    report_id=REPORT_ID,
    output_file="complete_report.pdf",
    workspace_id=WORKSPACE_ID,
    page_names=None  # All pages
)
```

**Use case:** Different report versions for different audiences

---

## Advanced Scenarios

### Example 7: Automated Daily Export

Create a scheduled task:

```python
# daily_export.py
from powerbi_export import PowerBIExporter
from datetime import datetime
import os

# Load credentials from environment variables
CLIENT_ID = os.getenv('POWERBI_CLIENT_ID')
CLIENT_SECRET = os.getenv('POWERBI_CLIENT_SECRET')
TENANT_ID = os.getenv('POWERBI_TENANT_ID')

# Date-stamped filenames
today = datetime.now().strftime('%Y-%m-%d')
csv_file = f"daily_report_{today}.csv"
pdf_file = f"daily_report_{today}.pdf"

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)

if exporter.authenticate():
    # Export data for analysis
    exporter.export_report_to_csv(
        report_id="daily-dashboard-id",
        output_file=csv_file,
        workspace_id="workspace-id"
    )
    
    # Export visual report
    exporter.export_report_to_pdf(
        report_id="daily-dashboard-id",
        output_file=pdf_file,
        workspace_id="workspace-id"
    )
    
    print(f"Daily export completed: {csv_file}, {pdf_file}")
else:
    print("Authentication failed")
```

**Schedule with cron (Linux/Mac):**
```bash
0 9 * * * /usr/bin/python3 /path/to/daily_export.py
```

**Schedule with Task Scheduler (Windows):**
- Create a task that runs daily at 9:00 AM
- Action: Start program `python.exe`
- Arguments: `C:\path\to\daily_export.py`

### Example 8: Export Multiple Reports

Process multiple reports in one script:

```python
from powerbi_export import PowerBIExporter

# Configuration
reports_config = [
    {
        "report_id": "sales-report-id",
        "workspace_id": "sales-workspace-id",
        "csv_file": "sales_data.csv",
        "pdf_file": "sales_report.pdf",
        "pages": ["Overview", "Regional Sales"]
    },
    {
        "report_id": "marketing-report-id",
        "workspace_id": "marketing-workspace-id",
        "csv_file": "marketing_data.csv",
        "pdf_file": "marketing_report.pdf",
        "pages": ["Campaign Results", "ROI Analysis"]
    },
    {
        "report_id": "finance-report-id",
        "workspace_id": "finance-workspace-id",
        "csv_file": "finance_data.csv",
        "pdf_file": "finance_report.pdf",
        "pages": None  # All pages
    }
]

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

for report in reports_config:
    print(f"\nProcessing {report['report_id']}...")
    
    # Export CSV
    exporter.export_report_to_csv(
        report_id=report['report_id'],
        output_file=report['csv_file'],
        workspace_id=report['workspace_id']
    )
    
    # Export PDF
    exporter.export_report_to_pdf(
        report_id=report['report_id'],
        output_file=report['pdf_file'],
        workspace_id=report['workspace_id'],
        page_names=report['pages']
    )

print("\nAll reports exported successfully!")
```

### Example 9: Error Handling and Retry Logic

Robust export with retry mechanism:

```python
from powerbi_export import PowerBIExporter
import time

def export_with_retry(exporter, report_id, output_file, 
                      workspace_id=None, max_retries=3, export_type='pdf'):
    """
    Export report with retry logic
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}...")
            
            if export_type == 'pdf':
                success = exporter.export_report_to_pdf(
                    report_id=report_id,
                    output_file=output_file,
                    workspace_id=workspace_id
                )
            else:
                success = exporter.export_report_to_csv(
                    report_id=report_id,
                    output_file=output_file,
                    workspace_id=workspace_id
                )
            
            if success:
                print(f"✓ Export succeeded on attempt {attempt + 1}")
                return True
            else:
                print(f"✗ Export failed on attempt {attempt + 1}")
                
        except Exception as e:
            print(f"✗ Exception on attempt {attempt + 1}: {str(e)}")
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 10  # Exponential backoff
            print(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    print(f"Failed after {max_retries} attempts")
    return False

# Usage
exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

export_with_retry(
    exporter=exporter,
    report_id="important-report-id",
    output_file="critical_report.pdf",
    workspace_id="workspace-id",
    export_type='pdf'
)
```

---

## Common Use Cases

### Use Case 1: Monthly Financial Reports

**Scenario:** Export monthly financial reports for board meetings

```python
# monthly_board_report.py
from powerbi_export import PowerBIExporter
from datetime import datetime

month_year = datetime.now().strftime('%B_%Y')
pdf_file = f"Board_Report_{month_year}.pdf"

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

# Export executive pages only
exporter.export_report_to_pdf(
    report_id="financial-report-id",
    output_file=pdf_file,
    workspace_id="finance-workspace",
    page_names=[
        "Executive Summary",
        "Revenue & Expenses",
        "Cash Flow",
        "Key Metrics"
    ]
)

print(f"Board report ready: {pdf_file}")
```

### Use Case 2: Data Pipeline Integration

**Scenario:** Export data for ETL pipeline

```python
# etl_export.py
from powerbi_export import PowerBIExporter
import pandas as pd
import sqlalchemy

# Export from Power BI
exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

exporter.export_report_to_csv(
    report_id="source-report-id",
    output_file="temp_data.csv",
    workspace_id="data-workspace"
)

# Load to database
df = pd.read_csv("temp_data.csv")

# Transform data
df['export_date'] = datetime.now()
df['source'] = 'PowerBI'

# Load to database
engine = sqlalchemy.create_engine('postgresql://user:pass@localhost/db')
df.to_sql('powerbi_exports', engine, if_exists='append', index=False)

print("Data successfully exported to database")
```

### Use Case 3: Email Distribution

**Scenario:** Email PDF reports to stakeholders

```python
# email_report.py
from powerbi_export import PowerBIExporter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Export report
exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()

pdf_file = "weekly_report.pdf"
exporter.export_report_to_pdf(
    report_id="weekly-report-id",
    output_file=pdf_file,
    workspace_id="reports-workspace"
)

# Email the report
msg = MIMEMultipart()
msg['From'] = "reports@company.com"
msg['To'] = "executives@company.com"
msg['Subject'] = "Weekly Performance Report"

body = "Please find attached this week's performance report."
msg.attach(MIMEText(body, 'plain'))

# Attach PDF
with open(pdf_file, 'rb') as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={pdf_file}')
    msg.attach(part)

# Send email
with smtplib.SMTP('smtp.company.com', 587) as server:
    server.starttls()
    server.login("username", "password")
    server.send_message(msg)

print("Report emailed successfully")
```

---

## Tips and Best Practices

### Performance Optimization

1. **CSV exports are faster than PDF** - use CSV when you only need data
2. **Export specific pages** instead of entire reports when possible
3. **Batch exports during off-peak hours** to reduce API load
4. **Cache authentication tokens** when making multiple exports

### Error Prevention

1. **Verify report and workspace IDs** before running exports
2. **Test with small reports first** before automating large exports
3. **Monitor API rate limits** to avoid throttling
4. **Implement retry logic** for production scripts

### Security

1. **Never hardcode credentials** in scripts
2. **Use environment variables** or secure key vaults
3. **Rotate client secrets regularly**
4. **Limit service principal permissions** to minimum required

### File Management

1. **Use timestamps in filenames** for automated exports
2. **Implement file retention policies** to manage disk space
3. **Compress old exports** to save storage
4. **Archive important reports** to separate locations

---

For more information, see the main [README.md](README.md) file.
