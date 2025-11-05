# Power BI Export Tool - Troubleshooting Guide

**Copyright 2025-2030 all rights reserved**  
**Author:** Ashutosh Sinha  
**Email:** ajsinha@gmail.com

---

## 🔧 "Cannot Import Config" - SOLVED! 

### The Problem
You see this error:
```
ERROR: Cannot import config.py
ModuleNotFoundError: No module named 'config'
```

### The Solution - Choose ONE method:

---

## ✅ Solution 1: Interactive Config Generator (EASIEST!)

```bash
python create_config.py
```

Follow the wizard - it will ask you for:
- CLIENT_ID
- CLIENT_SECRET  
- TENANT_ID
- REPORT_ID
- Other settings

Then run:
```bash
python run_export.py
```

**✓ No manual file editing required!**

---

## ✅ Solution 2: Use Direct Configuration (NO CONFIG FILE!)

**Step 1:** Open `run_export_direct.py` in any text editor

**Step 2:** Edit lines 19-25:
```python
CLIENT_ID = "your-client-id-here"      # ← Put your ID here
CLIENT_SECRET = "your-client-secret"   # ← Put your secret here  
TENANT_ID = "your-tenant-id"           # ← Put your tenant here
REPORT_ID = "your-report-id"           # ← Put your report here
```

**Step 3:** Run it:
```bash
python run_export_direct.py
```

**✓ Works immediately - no config.py needed!**

---

## ✅ Solution 3: Manual Config File (Traditional Way)

**Step 1:** Copy the template

```bash
# On Mac/Linux
cp config_template.py config.py

# On Windows (Command Prompt)
copy config_template.py config.py

# On Windows (PowerShell)
Copy-Item config_template.py config.py
```

**Step 2:** Edit config.py with your credentials

**Step 3:** Run:
```bash
python run_export.py
```

---

## ✅ Solution 4: Environment Variables (For CI/CD)

**Mac/Linux:**
```bash
export POWERBI_CLIENT_ID='abc-123'
export POWERBI_CLIENT_SECRET='your-secret'
export POWERBI_TENANT_ID='xyz-789'
export POWERBI_REPORT_ID='report-123'
python run_export_env.py
```

**Windows (PowerShell):**
```powershell
$env:POWERBI_CLIENT_ID='abc-123'
$env:POWERBI_CLIENT_SECRET='your-secret'
$env:POWERBI_TENANT_ID='xyz-789'
$env:POWERBI_REPORT_ID='report-123'
python run_export_env.py
```

**Windows (Command Prompt):**
```cmd
set POWERBI_CLIENT_ID=abc-123
set POWERBI_CLIENT_SECRET=your-secret
set POWERBI_TENANT_ID=xyz-789
set POWERBI_REPORT_ID=report-123
python run_export_env.py
```

---

## 📊 Which Method Should I Use?

| Method | Difficulty | Best For |
|--------|-----------|----------|
| **create_config.py** | ⭐ Easy | First time users |
| **run_export_direct.py** | ⭐⭐ Easy | Quick tests |
| **config.py (manual)** | ⭐⭐⭐ Medium | Regular use |
| **run_export_env.py** | ⭐⭐⭐⭐ Advanced | Automation/Docker |

---

## 🔍 Other Common Issues

### Issue: "No module named 'powerbi_export'"

**Solution:** Make sure you're in the right directory

```bash
# Check if powerbi_export.py exists
ls powerbi_export.py  # Mac/Linux
dir powerbi_export.py  # Windows

# If not found, navigate to correct folder
cd path/to/your/powerbi-tool
```

---

### Issue: "No module named 'requests'" or 'msal'

**Solution:** Install dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests msal pandas
```

---

### Issue: "Authentication failed"

**Checklist:**
- ✓ CLIENT_ID is correct (check Azure Portal)
- ✓ CLIENT_SECRET hasn't expired
- ✓ TENANT_ID is correct
- ✓ API permissions are granted
- ✓ Admin consent is given

---

### Issue: "Report not found"

**Solution 1:** Find your report ID

```python
from powerbi_export import PowerBIExporter

exporter = PowerBIExporter(CLIENT_ID, CLIENT_SECRET, TENANT_ID)
exporter.authenticate()
exporter.list_reports()  # Shows all report IDs
```

**Solution 2:** Check workspace access
- Service principal must be added to workspace
- Minimum role: Viewer

---

## 🎯 Quick Test

Test if everything is working:

```bash
python -c "from powerbi_export import PowerBIExporter; print('✓ Import works!')"
```

If you see "✓ Import works!" - you're ready!

---

## 📁 File Checklist

Make sure you have these files:

```
✓ powerbi_export.py       (main library)
✓ run_export.py           (uses config.py)
✓ run_export_direct.py    (no config needed)
✓ run_export_env.py       (uses environment variables)
✓ create_config.py        (config wizard)
✓ config_template.py      (template)
✓ requirements.txt        (dependencies)
```

---

## 🆘 Still Stuck?

**Email:** ajsinha@gmail.com

**Subject:** "Power BI Export - Config Import Issue"

**Include:**
1. Which script you're trying to run
2. Full error message
3. Python version: `python --version`
4. What you've tried

---

## ⚡ TL;DR - Fastest Solution

```bash
# Run this ONE command:
python create_config.py

# Then run:
python run_export.py

# Done! 🎉
```

---

**Pro Tip:** Use `run_export_direct.py` if you just want to test quickly without creating any config files!
