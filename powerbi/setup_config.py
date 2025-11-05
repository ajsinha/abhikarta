"""
Power BI Export Tool - Setup Script

Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This script helps you create a config.py file with your credentials.
"""

import os
import sys
import shutil

def create_config_file():
    """
    Interactive script to create config.py from template
    """
    print("\n" + "="*70)
    print("Power BI Export Tool - Configuration Setup")
    print("="*70)
    print("\nThis script will help you create your config.py file.")
    print("\nYou'll need the following from Azure AD:")
    print("  1. Application (Client) ID")
    print("  2. Client Secret")
    print("  3. Directory (Tenant) ID")
    print("  4. Your Power BI Report ID")
    print("  5. Workspace ID (optional)")
    print("\n" + "-"*70)
    
    # Check if config.py already exists
    if os.path.exists('config.py'):
        print("\n⚠️  WARNING: config.py already exists!")
        response = input("\nDo you want to overwrite it? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n✋ Setup cancelled. Your existing config.py was not modified.")
            return
        print("\n✓ Will overwrite existing config.py")
    
    # Check if template exists
    if not os.path.exists('config_template.py'):
        print("\n❌ ERROR: config_template.py not found!")
        print("Please make sure you have the config_template.py file in this directory.")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("Enter your Azure AD credentials")
    print("="*70)
    print("\n💡 Tip: You can leave fields empty and fill them in later by editing config.py")
    print()
    
    # Get user input
    client_id = input("Application (Client) ID: ").strip() or "your-client-id-here"
    client_secret = input("Client Secret: ").strip() or "your-client-secret-here"
    tenant_id = input("Directory (Tenant) ID: ").strip() or "your-tenant-id-here"
    
    print("\n" + "="*70)
    print("Enter your Power BI report details")
    print("="*70)
    print()
    
    report_id = input("Report ID: ").strip() or "your-report-id-here"
    workspace_id = input("Workspace ID (press Enter for 'My Workspace'): ").strip()
    
    # Handle workspace ID
    if workspace_id:
        workspace_id_value = f'"{workspace_id}"'
    else:
        workspace_id_value = "None"
    
    print("\n" + "="*70)
    print("Export options")
    print("="*70)
    print()
    
    print("Export format options:")
    print("  1. csv  - Export to CSV only")
    print("  2. pdf  - Export to PDF only")
    print("  3. both - Export to both CSV and PDF (default)")
    
    export_format = input("\nChoose format (1/2/3 or press Enter for 'both'): ").strip()
    format_map = {'1': 'csv', '2': 'pdf', '3': 'both', '': 'both'}
    export_format_value = format_map.get(export_format, 'both')
    
    csv_output = input("\nCSV output filename (default: powerbi_report_export.csv): ").strip()
    csv_output = csv_output or "powerbi_report_export.csv"
    
    pdf_output = input("PDF output filename (default: powerbi_report_export.pdf): ").strip()
    pdf_output = pdf_output or "powerbi_report_export.pdf"
    
    # Create config.py content
    config_content = f'''"""
Power BI Configuration

Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com
"""

# Azure AD Application Credentials
CLIENT_ID = "{client_id}"
CLIENT_SECRET = "{client_secret}"
TENANT_ID = "{tenant_id}"

# Power BI Report Details
WORKSPACE_ID = {workspace_id_value}  # Set to None for 'My Workspace' or provide workspace ID string
REPORT_ID = "{report_id}"

# Export Options
EXPORT_FORMAT = "{export_format_value}"  # Options: "csv", "pdf", "both"
CSV_OUTPUT_FILE = "{csv_output}"
PDF_OUTPUT_FILE = "{pdf_output}"

# Optional: Specific page(s) to export
PAGE_NAME = None  # For CSV: single page name as string or None for all
PAGE_NAMES = None  # For PDF: list of page names ['Page1', 'Page2'] or None for all
'''
    
    # Write config.py
    try:
        with open('config.py', 'w') as f:
            f.write(config_content)
        
        print("\n" + "="*70)
        print("✅ SUCCESS! Configuration file created")
        print("="*70)
        print(f"\n✓ File created: config.py")
        print(f"✓ Export format: {export_format_value.upper()}")
        print(f"✓ CSV output: {csv_output}")
        print(f"✓ PDF output: {pdf_output}")
        
        # Check if credentials are still placeholders
        if client_id == "your-client-id-here":
            print("\n⚠️  REMINDER: You need to edit config.py with your actual credentials!")
            print("   Your config.py still contains placeholder values.")
        
        print("\n" + "="*70)
        print("Next steps:")
        print("="*70)
        print("\n1. If you skipped any fields, edit config.py with your actual values")
        print("2. Make sure you've completed the Azure AD setup (see README.md)")
        print("3. Run the export script:")
        print("   python run_export.py")
        
        print("\n💡 Tip: config.py is in .gitignore to protect your credentials")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create config.py")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        create_config_file()
    except KeyboardInterrupt:
        print("\n\n✋ Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
