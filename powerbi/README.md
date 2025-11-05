# Power BI Report Exporter (CSV & PDF)

**Copyright 2025-2030 all rights reserved**  
**Author:** Ashutosh Sinha  
**Email:** ajsinha@gmail.com

---

A Python application to connect to Power BI and export reports to CSV and PDF formats using the Power BI REST API.

## Prerequisites

1. **Azure AD App Registration**: You need to register an application in Azure Active Directory
2. **Power BI Account**: Access to Power BI with reports you want to export
3. **Python 3.7+**: Installed on your system

## Setup Instructions

### Step 1: Register an Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations** > **New registration**
3. Fill in the details:
   - **Name**: PowerBI CSV Exporter (or any name you prefer)
   - **Supported account types**: Accounts in this organizational directory only
   - Click **Register**
4. Note down the **Application (client) ID** and **Directory (tenant) ID**

### Step 2: Create a Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description and set expiration
4. Click **Add**
5. **Copy the secret value immediately** (it won't be shown again)

### Step 3: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Power BI Service**
4. Choose **Delegated permissions** or **Application permissions** based on your needs:
   - For Service Principal (recommended): Select **Application permissions**
     - `Dataset.ReadWrite.All`
     - `Report.ReadWrite.All`
   - For User authentication: Select **Delegated permissions**
     - `Dataset.ReadWrite.All`
     - `Report.ReadWrite.All`
5. Click **Add permissions**
6. Click **Grant admin consent** (requires admin privileges)

### Step 4: Enable Power BI Service Principal (if using Application permissions)

1. Go to [Power BI Admin Portal](https://app.powerbi.com/admin-portal/tenantSettings)
2. Navigate to **Developer settings**
3. Enable **Service principals can use Power BI APIs**
4. Add your Azure AD app to the security group or select "Apply to entire organization"

### Step 5: Give Access to Workspace

1. Go to your Power BI workspace
2. Click **Access** (or workspace settings)
3. Add your service principal with at least **Viewer** role (Member or Admin for full access)

## Installation

1. Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install requests msal pandas
```

## Configuration

Edit the `powerbi_export.py` file and update the following variables in the `main()` function:

```python
# Your Azure AD app credentials
CLIENT_ID = "your-client-id-here"          # Application (client) ID
CLIENT_SECRET = "your-client-secret-here"  # Client secret value
TENANT_ID = "your-tenant-id-here"          # Directory (tenant) ID

# Your Power BI report details
WORKSPACE_ID = None  # Workspace ID or None for 'My Workspace'
REPORT_ID = "your-report-id-here"  # Report ID
OUTPUT_FILE = "powerbi_report_export.csv"  # Output filename
```

### Finding Your Report ID and Workspace ID

**Method 1: From Power BI URL**
- Open your report in Power BI Service
- Look at the URL: `https://app.powerbi.com/groups/{workspace-id}/reports/{report-id}/...`
- The IDs are in the URL structure

**Method 2: Use the script**
- Run the script with valid credentials
- It will list all workspaces and reports with their IDs

## Usage

### Basic Usage

Run the script:

```bash
python powerbi_export.py
```

The script will:
1. Authenticate with Azure AD
2. List available workspaces
3. List reports in the specified workspace
4. List pages in the specified report
5. Export the report to CSV format

### Advanced Usage

You can use the `PowerBIExporter` class in your own scripts:

```python
from powerbi_export import PowerBIExporter

# Initialize
exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)

# Authenticate
exporter.authenticate()

# List workspaces
workspaces = exporter.list_workspaces()

# List reports
reports = exporter.list_reports(workspace_id="your-workspace-id")

# Export to CSV - specific page
exporter.export_report_to_csv(
    report_id="your-report-id",
    output_file="output.csv",
    workspace_id="your-workspace-id",
    page_name="Page1"  # Optional: specific page name
)

# Export to PDF - entire report
exporter.export_report_to_pdf(
    report_id="your-report-id",
    output_file="output.pdf",
    workspace_id="your-workspace-id",
    page_names=None  # None for all pages
)

# Export to PDF - specific pages
exporter.export_report_to_pdf(
    report_id="your-report-id",
    output_file="output_selected.pdf",
    workspace_id="your-workspace-id",
    page_names=["Page1", "Page3", "Page5"]  # List of specific pages
)
```

## Features

- ✅ Azure AD authentication with service principal
- ✅ List all workspaces
- ✅ List all reports in a workspace
- ✅ List all pages in a report
- ✅ **Export reports to CSV format**
- ✅ **Export reports to PDF format**
- ✅ Export entire report or specific pages
- ✅ Automatic polling for export completion
- ✅ Error handling and status messages

## Export Format Comparison

| Feature | CSV | PDF |
|---------|-----|-----|
| **Best For** | Data analysis, Excel import | Presentation, printing, sharing |
| **File Size** | Smaller | Larger |
| **Visual Fidelity** | Data only | Preserves layout and design |
| **Export Time** | Faster | Slower |
| **Page Selection** | Single page | Multiple pages |
| **Data Structure** | Tabular/structured | Visual/formatted |

**When to use CSV:**
- You need raw data for analysis
- Importing into Excel, databases, or data tools
- File size is a concern
- Quick exports needed

**When to use PDF:**
- Sharing reports with stakeholders
- Preserving visual design and layout
- Printing physical copies
- Complete multi-page reports needed

## Limitations

### CSV Export
- CSV export format has some limitations compared to other formats
- Some visual types may not export well to CSV
- Only tabular data is exported

### PDF Export
- PDF exports may take longer than CSV exports
- Large reports with many pages may timeout (increase max_attempts if needed)
- PDF quality depends on report design and complexity

### General
- Large reports may take time to export
- The API has rate limits (check Microsoft documentation)
- Some report types may not be exportable

## Troubleshooting

### Authentication Failed
- Verify your CLIENT_ID, CLIENT_SECRET, and TENANT_ID are correct
- Ensure the client secret hasn't expired
- Check that API permissions are granted and admin consent is given

### Report Not Found
- Verify the REPORT_ID is correct
- Ensure the service principal has access to the workspace
- Check that the report exists and isn't deleted

### Export Failed
- Some report types cannot be exported to CSV
- Check that the report contains exportable visuals
- Verify you have the necessary permissions

### Service Principal Access Denied
- Ensure service principals are enabled in Power BI tenant settings
- Verify the service principal is added to the workspace with appropriate permissions
- Check that "Service principals can use Power BI APIs" is enabled

## API Documentation

For more information, refer to:
- [Power BI REST API Documentation](https://learn.microsoft.com/en-us/rest/api/power-bi/)
- [Export Reports API](https://learn.microsoft.com/en-us/rest/api/power-bi/reports/export-to-file)

## License

This code is provided as-is for educational and development purposes.
