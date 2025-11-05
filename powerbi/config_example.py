"""
Power BI Configuration File - EXAMPLE

Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

INSTRUCTIONS:
This is an example config file. Replace the placeholder values below with your
actual Azure AD and Power BI credentials.

IMPORTANT: This file contains sensitive credentials. 
- Do NOT commit this file to version control (it's in .gitignore)
- Keep this file secure
- Rotate your client secrets regularly
"""

# =============================================================================
# AZURE AD APPLICATION CREDENTIALS (Required)
# =============================================================================
# Get these from Azure Portal > Azure Active Directory > App registrations

CLIENT_ID = "your-client-id-here"          # Application (client) ID
CLIENT_SECRET = "your-client-secret-here"  # Client secret value  
TENANT_ID = "your-tenant-id-here"          # Directory (tenant) ID


# =============================================================================
# POWER BI REPORT DETAILS (Required)
# =============================================================================

# Workspace ID: 
#   - Set to None to use "My Workspace"
#   - Or provide your workspace ID as a string: "abc123-def456-..."
WORKSPACE_ID = None  

# Report ID: The ID of the report you want to export
# Find this in the Power BI URL: 
# https://app.powerbi.com/groups/{workspace-id}/reports/{report-id}/...
REPORT_ID = "your-report-id-here"


# =============================================================================
# EXPORT OPTIONS
# =============================================================================

# Export Format: Choose what format(s) to export
# Options: "csv", "pdf", "both"
EXPORT_FORMAT = "both"

# Output Filenames
CSV_OUTPUT_FILE = "powerbi_report_export.csv"
PDF_OUTPUT_FILE = "powerbi_report_export.pdf"


# =============================================================================
# PAGE SELECTION (Optional)
# =============================================================================

# For CSV Export: Export a specific page (single page only)
# Set to None to export all data, or specify a page name:
# PAGE_NAME = "Sales Dashboard"
PAGE_NAME = None

# For PDF Export: Export specific pages (can be multiple)
# Set to None to export all pages, or specify a list:
# PAGE_NAMES = ["Executive Summary", "Details", "Charts"]
PAGE_NAMES = None


# =============================================================================
# QUICK START GUIDE
# =============================================================================
"""
1. Replace all "your-xxx-here" values above with your actual credentials
2. Set your REPORT_ID and optionally WORKSPACE_ID
3. Choose your EXPORT_FORMAT and output filenames
4. Save this file
5. Run: python run_export.py

For detailed setup instructions, see README.md
For usage examples, see USAGE_EXAMPLES.md
For quick reference, see QUICK_REFERENCE.md
"""
