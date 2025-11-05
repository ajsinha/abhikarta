# Power BI Export Tool - Project Summary

**Copyright 2025-2030 all rights reserved**  
**Author:** Ashutosh Sinha  
**Email:** ajsinha@gmail.com  
**Version:** 2.0.0

---

## 📦 Project Overview

This project provides a Python-based solution for exporting Power BI reports to CSV and PDF formats using the Power BI REST API with Azure AD authentication.

---

## 📁 Project Files

### Core Application Files

1. **powerbi_export.py** ⭐
   - Main Python class with all functionality
   - Includes authentication, listing, CSV export, and PDF export methods
   - Comprehensive error handling
   - **Key Methods:**
     - `authenticate()` - Azure AD authentication
     - `list_workspaces()` - List all workspaces
     - `list_reports()` - List reports in a workspace
     - `get_report_pages()` - Get pages in a report
     - `export_report_to_csv()` - Export to CSV format
     - `export_report_to_pdf()` - **NEW** Export to PDF format

2. **run_export.py**
   - Ready-to-use script that loads credentials from config file
   - Supports CSV, PDF, or both export formats
   - Progress tracking and user-friendly output
   - Error handling with clear messages

3. **config_template.py**
   - Configuration template file
   - Contains all necessary settings
   - Copy to `config.py` and fill in your credentials
   - **Settings:**
     - Azure AD credentials
     - Report/workspace IDs
     - Export format selection
     - Output file names
     - Page selection options

4. **requirements.txt**
   - Python dependencies
   - Required packages: requests, msal, pandas

---

### Documentation Files

5. **README.md** ⭐
   - Complete setup and installation guide
   - Step-by-step Azure AD configuration
   - Usage instructions
   - Troubleshooting section
   - Export format comparison
   - API documentation links

6. **USAGE_EXAMPLES.md** ⭐
   - 9 detailed practical examples
   - Quick start examples
   - CSV export scenarios
   - PDF export scenarios
   - Advanced automation scenarios
   - Common use cases with code
   - Tips and best practices

7. **QUICK_REFERENCE.md**
   - One-page cheat sheet
   - Quick start commands
   - Configuration templates
   - Code snippets
   - Troubleshooting table
   - Common tasks

8. **CHANGELOG.md**
   - Version history
   - Feature additions
   - Changes and improvements
   - Planned future features

9. **LICENSE**
   - Copyright information
   - Usage terms
   - Contact information

10. **.gitignore**
    - Protects sensitive files
    - Excludes credentials and outputs
    - Python and IDE-specific exclusions

---

## ✨ New Features in Version 2.0.0

### PDF Export Support
- **New Method:** `export_report_to_pdf()`
- Export entire reports or specific pages
- Multiple page selection support
- Enhanced timeout handling for large reports
- Detailed error reporting

### Enhanced Configuration
- **Export Format Selection:** Choose CSV, PDF, or both
- **Flexible Page Selection:**
  - CSV: Single page (`PAGE_NAME`)
  - PDF: Multiple pages (`PAGE_NAMES`)
- Date-stamped filenames support
- Better error messages

### Improved Documentation
- Comprehensive usage examples
- Quick reference guide
- Export format comparison
- Real-world use cases
- Automation examples

### Copyright & Licensing
- Copyright headers in all Python files
- Formal LICENSE file
- Contact information
- Version tracking

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Azure AD Setup
1. Register app in Azure Portal
2. Create client secret
3. Grant Power BI API permissions
4. Enable service principal in Power BI

### 3. Configure Application
```bash
cp config_template.py config.py
# Edit config.py with your credentials
```

### 4. Run Export
```bash
python run_export.py
```

---

## 📊 Export Formats

### CSV Export
- **Best For:** Data analysis, Excel import, ETL pipelines
- **Speed:** Fast
- **Size:** Compact
- **Content:** Tabular data only
- **Pages:** Single page export

### PDF Export
- **Best For:** Presentations, sharing, printing, archiving
- **Speed:** Slower (requires rendering)
- **Size:** Larger (includes visuals)
- **Content:** Complete visual layout
- **Pages:** Multiple pages in single file

---

## 🔑 Key Capabilities

### Authentication
- ✅ Azure AD service principal authentication
- ✅ Token management
- ✅ Secure credential handling

### Discovery
- ✅ List all accessible workspaces
- ✅ List reports in any workspace
- ✅ Enumerate pages in reports

### Export
- ✅ CSV export (tabular data)
- ✅ PDF export (visual reports)
- ✅ Single page selection
- ✅ Multiple page selection
- ✅ Full report export

### Error Handling
- ✅ Comprehensive error messages
- ✅ API response parsing
- ✅ Timeout management
- ✅ Status tracking

---

## 📖 Usage Patterns

### Simple Export
```python
exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()
exporter.export_report_to_pdf(REPORT_ID, "output.pdf")
```

### Automated Daily Export
```python
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
exporter.export_report_to_pdf(
    REPORT_ID, 
    f"daily_report_{today}.pdf"
)
```

### Multiple Report Processing
```python
for report in report_list:
    exporter.export_report_to_csv(
        report['id'], 
        f"{report['name']}.csv"
    )
```

---

## 🛠️ Development

### Project Structure
```
powerbi-export-tool/
├── powerbi_export.py      # Core library
├── run_export.py          # Main executable
├── config_template.py     # Configuration template
├── requirements.txt       # Dependencies
├── README.md             # Main documentation
├── USAGE_EXAMPLES.md     # Detailed examples
├── QUICK_REFERENCE.md    # Cheat sheet
├── CHANGELOG.md          # Version history
├── LICENSE               # Copyright info
└── .gitignore           # Git exclusions
```

### Technology Stack
- **Language:** Python 3.7+
- **Authentication:** MSAL (Microsoft Authentication Library)
- **HTTP Client:** requests
- **Data Processing:** pandas
- **API:** Power BI REST API v1.0

---

## 🎯 Use Cases

1. **Automated Reporting**
   - Schedule daily/weekly exports
   - Email reports to stakeholders
   - Archive historical snapshots

2. **Data Analysis**
   - Export data for Excel analysis
   - Feed ETL pipelines
   - Generate CSV for databases

3. **Presentation Distribution**
   - Create PDF reports for meetings
   - Share formatted reports externally
   - Print physical copies

4. **Compliance & Archiving**
   - Maintain report archives
   - Document historical data
   - Audit trail creation

---

## 🔒 Security Considerations

### Credentials
- Never commit config.py to version control
- Use environment variables in production
- Rotate secrets regularly
- Apply principle of least privilege

### Permissions
- Grant minimum necessary API permissions
- Restrict workspace access
- Monitor service principal usage
- Review access logs regularly

### Best Practices
- Enable MFA on admin accounts
- Use dedicated service principals
- Implement retry logic with backoff
- Log all export operations

---

## 📈 Future Enhancements

### Planned Features
- Excel (.xlsx) export support
- PowerPoint (.pptx) export support
- Image (PNG/JPEG) export
- Email integration
- Cloud storage upload (Azure/AWS/GCP)
- Export scheduling UI
- Batch processing improvements
- Performance monitoring

### Community Requests
- Want a feature? Email: ajsinha@gmail.com

---

## 🤝 Support

### Getting Help
- **Email:** ajsinha@gmail.com
- **Subject Format:** "Power BI Export Tool - [Your Issue]"
- **Response Time:** Best effort

### Common Issues
- Authentication problems → Check credentials and permissions
- Export failures → Verify report IDs and access
- Timeout errors → Increase max_attempts parameter
- API limits → Space out requests, use off-peak hours

---

## 📝 Copyright

**Copyright 2025-2030 all rights reserved**  
**Author:** Ashutosh Sinha  
**Email:** ajsinha@gmail.com

This software is provided for educational and development purposes.
All rights reserved.

---

## 🙏 Acknowledgments

- Microsoft Power BI REST API documentation
- MSAL Python library developers
- Python requests library contributors
- The Power BI community

---

## 📅 Version History

- **v2.0.0** (Current) - Added PDF export, enhanced docs, copyright
- **v1.0.0** - Initial release with CSV export

---

**Thank you for using Power BI Export Tool!**

For the latest updates and documentation, keep all project files together.
