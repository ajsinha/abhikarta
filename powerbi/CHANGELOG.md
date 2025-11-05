# Changelog

All notable changes to Power BI Report Exporter will be documented in this file.

**Copyright 2025-2030 all rights reserved**  
**Author:** Ashutosh Sinha  
**Email:** ajsinha@gmail.com

---

## [Version 2.0.0] - 2025-01-XX

### Added
- **PDF Export Support**: New `export_report_to_pdf()` method for exporting reports to PDF format
- **Multi-format Export**: Support for exporting to both CSV and PDF in a single run
- **Flexible Page Selection**: 
  - CSV: Export single page or entire report
  - PDF: Export multiple specific pages or entire report
- **Enhanced Configuration**: New config options for export format selection
- **Comprehensive Documentation**: 
  - Added USAGE_EXAMPLES.md with practical scenarios
  - Updated README.md with PDF export instructions
  - Added export format comparison guide
- **Copyright Information**: Added copyright headers to all source files
- **LICENSE File**: Added formal license and copyright information

### Changed
- Updated `run_export.py` to support both CSV and PDF exports
- Enhanced error handling for PDF exports with detailed error messages
- Increased timeout for PDF exports (60 attempts vs 30 for CSV)
- Updated configuration template with new export options

### Technical Details
- PDF exports use the Power BI REST API ExportTo endpoint with format "PDF"
- Supports multiple page export in a single PDF file
- Enhanced polling mechanism with longer wait times for PDF generation
- Improved error reporting with API response details

---

## [Version 1.0.0] - 2025-01-XX

### Added
- Initial release
- Azure AD authentication with service principal
- CSV export functionality
- Workspace and report listing
- Report page enumeration
- Basic error handling
- Configuration file support
- README documentation

### Features
- Connect to Power BI using REST API
- Export reports to CSV format
- List workspaces and reports
- Get report page information
- Support for both 'My Workspace' and shared workspaces

---

## Upcoming Features

### Planned for Future Versions
- Excel (XLSX) export support
- PowerPoint (PPTX) export support
- Image (PNG) export support
- Batch export of multiple reports
- Email integration for automated distribution
- Cloud storage integration (Azure Blob, AWS S3, Google Drive)
- Report scheduling and automation
- Export history tracking
- Performance metrics and logging

---

## Support

For questions or support:
- Email: ajsinha@gmail.com
- Subject: "Power BI Export Tool - [Your Issue]"
