"""
Power BI Report Exporter - Export reports to CSV and PDF formats

Copyright 2025-2030 all rights reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

This script connects to Power BI using the REST API and exports report data to CSV or PDF format.
Requires Azure AD app registration with appropriate Power BI API permissions.
"""

import requests
import msal
import pandas as pd
import time
import json
from typing import Optional, Dict, Any


class PowerBIExporter:
    """
    A class to handle Power BI authentication and report export operations.
    """
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        """
        Initialize the Power BI exporter with Azure AD credentials.
        
        Args:
            client_id: Azure AD application (client) ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://analysis.windows.net/powerbi/api/.default"]
        self.access_token = None
        self.base_url = "https://api.powerbi.com/v1.0/myorg"
        
    def authenticate(self) -> bool:
        """
        Authenticate with Azure AD and obtain an access token.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                print("Authentication successful!")
                return True
            else:
                print(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get the HTTP headers for API requests.
        
        Returns:
            dict: Headers including authorization token
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def list_workspaces(self) -> Optional[list]:
        """
        List all available workspaces.
        
        Returns:
            list: List of workspaces or None if failed
        """
        try:
            url = f"{self.base_url}/groups"
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            workspaces = response.json()["value"]
            print(f"\nFound {len(workspaces)} workspace(s):")
            for ws in workspaces:
                print(f"  - {ws['name']} (ID: {ws['id']})")
            
            return workspaces
            
        except Exception as e:
            print(f"Error listing workspaces: {str(e)}")
            return None
    
    def list_reports(self, workspace_id: Optional[str] = None) -> Optional[list]:
        """
        List all reports in a workspace or in 'My Workspace'.
        
        Args:
            workspace_id: Optional workspace ID. If None, uses 'My Workspace'
            
        Returns:
            list: List of reports or None if failed
        """
        try:
            if workspace_id:
                url = f"{self.base_url}/groups/{workspace_id}/reports"
            else:
                url = f"{self.base_url}/reports"
            
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            reports = response.json()["value"]
            print(f"\nFound {len(reports)} report(s):")
            for report in reports:
                print(f"  - {report['name']} (ID: {report['id']})")
            
            return reports
            
        except Exception as e:
            print(f"Error listing reports: {str(e)}")
            return None
    
    def export_report_to_csv(
        self, 
        report_id: str, 
        output_file: str,
        workspace_id: Optional[str] = None,
        page_name: Optional[str] = None
    ) -> bool:
        """
        Export a Power BI report to CSV format.
        
        Args:
            report_id: The report ID to export
            output_file: Path to save the CSV file
            workspace_id: Optional workspace ID
            page_name: Optional specific page name to export
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Step 1: Initiate export
            print(f"\nInitiating export for report {report_id}...")
            
            if workspace_id:
                export_url = f"{self.base_url}/groups/{workspace_id}/reports/{report_id}/ExportTo"
            else:
                export_url = f"{self.base_url}/reports/{report_id}/ExportTo"
            
            export_request = {
                "format": "CSV"
            }
            
            if page_name:
                export_request["powerBIReportConfiguration"] = {
                    "pages": [{"pageName": page_name}]
                }
            
            response = requests.post(
                export_url,
                headers=self.get_headers(),
                json=export_request
            )
            response.raise_for_status()
            
            export_id = response.json()["id"]
            print(f"Export initiated with ID: {export_id}")
            
            # Step 2: Poll for export status
            if workspace_id:
                status_url = f"{self.base_url}/groups/{workspace_id}/reports/{report_id}/exports/{export_id}"
            else:
                status_url = f"{self.base_url}/reports/{report_id}/exports/{export_id}"
            
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(2)  # Wait 2 seconds between checks
                
                status_response = requests.get(status_url, headers=self.get_headers())
                status_response.raise_for_status()
                
                status = status_response.json()
                export_status = status.get("status")
                
                print(f"Export status: {export_status}")
                
                if export_status == "Succeeded":
                    # Step 3: Download the file
                    download_url = f"{status_url}/file"
                    download_response = requests.get(download_url, headers=self.get_headers())
                    download_response.raise_for_status()
                    
                    with open(output_file, 'wb') as f:
                        f.write(download_response.content)
                    
                    print(f"✓ Report exported successfully to: {output_file}")
                    return True
                    
                elif export_status == "Failed":
                    print(f"Export failed: {status.get('error', 'Unknown error')}")
                    return False
                
                attempt += 1
            
            print("Export timed out")
            return False
            
        except Exception as e:
            print(f"Error exporting report: {str(e)}")
            return False
    
    def export_report_to_pdf(
        self, 
        report_id: str, 
        output_file: str,
        workspace_id: Optional[str] = None,
        page_names: Optional[list] = None
    ) -> bool:
        """
        Export a Power BI report to PDF format.
        
        Args:
            report_id: The report ID to export
            output_file: Path to save the PDF file
            workspace_id: Optional workspace ID
            page_names: Optional list of specific page names to export
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Step 1: Initiate export
            print(f"\nInitiating PDF export for report {report_id}...")
            
            if workspace_id:
                export_url = f"{self.base_url}/groups/{workspace_id}/reports/{report_id}/ExportTo"
            else:
                export_url = f"{self.base_url}/reports/{report_id}/ExportTo"
            
            export_request = {
                "format": "PDF"
            }
            
            # Configure specific pages if requested
            if page_names:
                export_request["powerBIReportConfiguration"] = {
                    "pages": [{"pageName": name} for name in page_names]
                }
            
            response = requests.post(
                export_url,
                headers=self.get_headers(),
                json=export_request
            )
            response.raise_for_status()
            
            export_id = response.json()["id"]
            print(f"PDF export initiated with ID: {export_id}")
            
            # Step 2: Poll for export status
            if workspace_id:
                status_url = f"{self.base_url}/groups/{workspace_id}/reports/{report_id}/exports/{export_id}"
            else:
                status_url = f"{self.base_url}/reports/{report_id}/exports/{export_id}"
            
            max_attempts = 60  # PDF exports can take longer
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(3)  # Wait 3 seconds between checks for PDF
                
                status_response = requests.get(status_url, headers=self.get_headers())
                status_response.raise_for_status()
                
                status = status_response.json()
                export_status = status.get("status")
                
                print(f"PDF export status: {export_status} (attempt {attempt + 1}/{max_attempts})")
                
                if export_status == "Succeeded":
                    # Step 3: Download the PDF file
                    download_url = f"{status_url}/file"
                    download_response = requests.get(download_url, headers=self.get_headers())
                    download_response.raise_for_status()
                    
                    with open(output_file, 'wb') as f:
                        f.write(download_response.content)
                    
                    print(f"✓ Report exported successfully to PDF: {output_file}")
                    return True
                    
                elif export_status == "Failed":
                    error_info = status.get("error', {}")
                    error_msg = error_info.get('message', 'Unknown error')
                    print(f"PDF export failed: {error_msg}")
                    return False
                
                attempt += 1
            
            print("PDF export timed out")
            return False
            
        except Exception as e:
            print(f"Error exporting report to PDF: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"Error details: {error_detail}")
                except:
                    print(f"Response status code: {e.response.status_code}")
            return False
    
    def get_report_pages(self, report_id: str, workspace_id: Optional[str] = None) -> Optional[list]:
        """
        Get list of pages in a report.
        
        Args:
            report_id: The report ID
            workspace_id: Optional workspace ID
            
        Returns:
            list: List of page names or None if failed
        """
        try:
            if workspace_id:
                url = f"{self.base_url}/groups/{workspace_id}/reports/{report_id}/pages"
            else:
                url = f"{self.base_url}/reports/{report_id}/pages"
            
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            
            pages = response.json()["value"]
            print(f"\nFound {len(pages)} page(s):")
            for page in pages:
                print(f"  - {page['name']} (Display Name: {page['displayName']})")
            
            return pages
            
        except Exception as e:
            print(f"Error getting report pages: {str(e)}")
            return None


def main():
    """
    Main function demonstrating usage of the PowerBIExporter class.
    """
    
    # Configuration - Replace with your Azure AD app credentials
    CLIENT_ID = "your-client-id-here"
    CLIENT_SECRET = "your-client-secret-here"
    TENANT_ID = "your-tenant-id-here"
    
    # Report details - Replace with your report information
    WORKSPACE_ID = None  # Set to None for 'My Workspace' or provide workspace ID
    REPORT_ID = "your-report-id-here"
    CSV_OUTPUT_FILE = "powerbi_report_export.csv"
    PDF_OUTPUT_FILE = "powerbi_report_export.pdf"
    
    # Initialize exporter
    exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
    
    # Authenticate
    if not exporter.authenticate():
        print("Failed to authenticate. Please check your credentials.")
        return
    
    # List available workspaces
    print("\n" + "="*50)
    print("LISTING WORKSPACES")
    print("="*50)
    exporter.list_workspaces()
    
    # List reports in workspace
    print("\n" + "="*50)
    print("LISTING REPORTS")
    print("="*50)
    exporter.list_reports(WORKSPACE_ID)
    
    # Get report pages (optional)
    print("\n" + "="*50)
    print("LISTING REPORT PAGES")
    print("="*50)
    exporter.get_report_pages(REPORT_ID, WORKSPACE_ID)
    
    # Export report to CSV
    print("\n" + "="*50)
    print("EXPORTING REPORT TO CSV")
    print("="*50)
    csv_success = exporter.export_report_to_csv(
        report_id=REPORT_ID,
        output_file=CSV_OUTPUT_FILE,
        workspace_id=WORKSPACE_ID,
        page_name=None  # Set to specific page name if needed
    )
    
    # Export report to PDF
    print("\n" + "="*50)
    print("EXPORTING REPORT TO PDF")
    print("="*50)
    pdf_success = exporter.export_report_to_pdf(
        report_id=REPORT_ID,
        output_file=PDF_OUTPUT_FILE,
        workspace_id=WORKSPACE_ID,
        page_names=None  # Set to list of page names if needed, e.g., ["Page1", "Page2"]
    )
    
    # Summary
    print("\n" + "="*50)
    print("EXPORT SUMMARY")
    print("="*50)
    if csv_success:
        print(f"✓ CSV export saved to: {CSV_OUTPUT_FILE}")
    else:
        print(f"✗ CSV export failed")
    
    if pdf_success:
        print(f"✓ PDF export saved to: {PDF_OUTPUT_FILE}")
    else:
        print(f"✗ PDF export failed")


if __name__ == "__main__":
    main()
