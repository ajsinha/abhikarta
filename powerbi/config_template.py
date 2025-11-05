"""
Power BI Configuration Template

Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

# Copy this file to config.py and fill in your actual values
# Make sure to add config.py to .gitignore to keep credentials secure

# Azure AD Application Credentials
CLIENT_ID = "your-client-id-here"
CLIENT_SECRET = "your-client-secret-here"
TENANT_ID = "your-tenant-id-here"

# Power BI Report Details
WORKSPACE_ID = None  # Set to None for 'My Workspace' or provide workspace ID string
REPORT_ID = "your-report-id-here"

# Export Options
EXPORT_FORMAT = "both"  # Options: "csv", "pdf", "both"
CSV_OUTPUT_FILE = "powerbi_report_export.csv"
PDF_OUTPUT_FILE = "powerbi_report_export.pdf"

# Optional: Specific page(s) to export
PAGE_NAME = None  # For CSV: single page name as string or None for all
PAGE_NAMES = None  # For PDF: list of page names ['Page1', 'Page2'] or None for all
