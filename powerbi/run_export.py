"""
Power BI Export Script using config file

Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This version loads credentials from config.py for better security
Supports both CSV and PDF export formats
"""

from powerbi_export import PowerBIExporter

# Try to import config, fallback to template if not found
try:
    import config
    CLIENT_ID = config.CLIENT_ID
    CLIENT_SECRET = config.CLIENT_SECRET
    TENANT_ID = config.TENANT_ID
    WORKSPACE_ID = config.WORKSPACE_ID
    REPORT_ID = config.REPORT_ID
    EXPORT_FORMAT = getattr(config, 'EXPORT_FORMAT', 'both')
    CSV_OUTPUT_FILE = getattr(config, 'CSV_OUTPUT_FILE', 'powerbi_report_export.csv')
    PDF_OUTPUT_FILE = getattr(config, 'PDF_OUTPUT_FILE', 'powerbi_report_export.pdf')
    PAGE_NAME = getattr(config, 'PAGE_NAME', None)
    PAGE_NAMES = getattr(config, 'PAGE_NAMES', None)
except ImportError:
    print("ERROR: config.py not found!")
    print("Please copy config_template.py to config.py and fill in your credentials.")
    print("Example: cp config_template.py config.py")
    exit(1)


def main():
    """
    Main execution function using configuration from config.py
    Supports CSV, PDF, or both export formats
    """
    
    # Validate configuration
    if CLIENT_ID == "your-client-id-here":
        print("ERROR: Please update config.py with your actual credentials!")
        print("The config file still contains template values.")
        exit(1)
    
    print("Power BI Report Export Tool")
    print("=" * 60)
    print(f"Export Format: {EXPORT_FORMAT.upper()}")
    print("=" * 60)
    
    # Initialize exporter
    exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # Authenticate
    print("\n[1/5] Authenticating...")
    if not exporter.authenticate():
        print("❌ Failed to authenticate. Please check your credentials.")
        return
    
    # List available workspaces
    print("\n[2/5] Listing workspaces...")
    print("-" * 60)
    exporter.list_workspaces()
    
    # List reports in workspace
    print("\n[3/5] Listing reports...")
    print("-" * 60)
    exporter.list_reports(WORKSPACE_ID)
    
    # Get report pages
    print("\n[4/5] Listing report pages...")
    print("-" * 60)
    exporter.get_report_pages(REPORT_ID, WORKSPACE_ID)
    
    # Export based on format
    print("\n[5/5] Exporting report...")
    print("-" * 60)
    
    csv_success = False
    pdf_success = False
    
    # Export to CSV
    if EXPORT_FORMAT.lower() in ['csv', 'both']:
        print("\n📄 Exporting to CSV...")
        csv_success = exporter.export_report_to_csv(
            report_id=REPORT_ID,
            output_file=CSV_OUTPUT_FILE,
            workspace_id=WORKSPACE_ID,
            page_name=PAGE_NAME
        )
    
    # Export to PDF
    if EXPORT_FORMAT.lower() in ['pdf', 'both']:
        print("\n📕 Exporting to PDF...")
        pdf_success = exporter.export_report_to_pdf(
            report_id=REPORT_ID,
            output_file=PDF_OUTPUT_FILE,
            workspace_id=WORKSPACE_ID,
            page_names=PAGE_NAMES
        )
    
    # Summary
    print("\n" + "=" * 60)
    print("EXPORT SUMMARY")
    print("=" * 60)
    
    if EXPORT_FORMAT.lower() in ['csv', 'both']:
        if csv_success:
            print(f"✅ CSV export saved to: {CSV_OUTPUT_FILE}")
        else:
            print(f"❌ CSV export failed")
    
    if EXPORT_FORMAT.lower() in ['pdf', 'both']:
        if pdf_success:
            print(f"✅ PDF export saved to: {PDF_OUTPUT_FILE}")
        else:
            print(f"❌ PDF export failed")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
