# Seattle ADU Permit Readiness Checker (MVP)

A lightweight, config-driven screening tool to help Seattle homeowners assess whether an ADU (Accessory Dwelling Unit) project is **Likely**, **Possible**, or **Unlikely** based on self-reported inputs and representative Seattle SDCI rules.

**⚠️ This tool is informational only and is not a permit determination or legal advice.**

---

## Table of Contents

- [Phase 1 Scope](#phase-1-scope)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Quick Start Summary](#quick-start-summary)
- [Development Workflow](#development-workflow)
- [How It Works](#how-it-works)
- [Editing Rules](#editing-rules-no-code-changes-required)
- [Input Validation](#input-validation)
- [Troubleshooting](#troubleshooting)
- [Next Steps for Users](#next-steps-for-users)

---



## Phase 1 Scope

- ✅ **Seattle only** (single-city implementation)
- ✅ **Config-driven rules engine** (JSON-based, editable without code changes)
- ✅ **Simple questionnaire** with validation
- ✅ **Plain-English results** with clear reasons and next steps
- ✅ **No deployment required** (runs locally)

---

## Project Structure

```
seattle-adu-screening-/
├── app.py                      # Flask backend
├── engine.py                   # Rules evaluation engine
├── seattle_phase1_rules.json   # Editable ruleset
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── templates/
│   ├── form.html              # User questionnaire
│   └── result.html            # Results display
├── logic_overview.md          # Decision logic documentation
└── README.md                  # This file
```

---

## 🚀 Getting Started

### First Time Setup?

Follow the complete [Setup Instructions](#setup-instructions) below (Steps 1-7).

**Estimated time:** 10-15 minutes

### Returning User?

```bash
cd seattle-adu-screening-
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
python app.py
# Open http://127.0.0.1:5000
```

**Estimated time:** 30 seconds

---

## Setup Instructions

### Step 1: Verify Python Installation

Before starting, ensure Python 3.7 or higher is installed on your system.

**Check Python version:**

```bash
python --version
```

or

```bash
python3 --version
```

**Expected output:** `Python 3.7.x` or higher

**If Python is not installed:**
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** `brew install python3` or download from python.org
- **Linux:** `sudo apt-get install python3 python3-pip` (Debian/Ubuntu)

---

### Step 2: Clone the Repository

**Option A: Using Git (Recommended)**

```bash
# Clone the repository
git clone https://github.com/DominicTurn/seattle-adu-screening-.git

# Navigate into the project directory
cd seattle-adu-screening-

# Switch to the phase1-mvp branch
git checkout phase1-mvp
```

**Option B: Download ZIP**

1. Visit: [https://github.com/DominicTurn/seattle-adu-screening-](https://github.com/DominicTurn/seattle-adu-screening-)
2. Click **Code** → **Download ZIP**
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

---

### Step 3: Create a Virtual Environment (Recommended)

Using a virtual environment isolates project dependencies from your system Python.

**On Windows:**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**On macOS/Linux:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**You'll see `(venv)` prefix in your terminal when activated.**

---

### Step 4: Install Dependencies

With the virtual environment activated:

**Option A: Using requirements.txt (Recommended)**

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all dependencies from requirements.txt
pip install -r requirements.txt
```

**Option B: Manual installation**

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install Flask
pip install flask
```

**Verify installation:**

```bash
pip list
```

You should see `Flask` and its dependencies (Werkzeug, Jinja2, etc.) listed.

---

### Step 5: Run the Application

**Start the Flask development server:**

```bash
python app.py
```

**Expected output:**

```
INFO - Rules loaded successfully.
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

### Step 6: Access the Application

Open your web browser and navigate to:

**http://127.0.0.1:5000**

or

**http://localhost:5000**

You should see the Seattle ADU screening questionnaire.

---

### Step 7: Stop the Application

To stop the Flask server:

- Press `CTRL+C` in the terminal

**Deactivate virtual environment (when done):**

```bash
deactivate
```

---

## Quick Start Summary

```bash
# 1. Check Python
python --version

# 2. Clone and checkout branch
git clone https://github.com/DominicTurn/seattle-adu-screening-.git
cd seattle-adu-screening-
git checkout phase1-mvp

# 3. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Run application
python app.py

# 6. Open browser → http://127.0.0.1:5000
```

---

## Development Workflow

### Starting Work

```bash
# Navigate to project
cd seattle-adu-screening-

# Pull latest changes
git pull origin phase1-mvp

# Activate virtual environment
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Start development server
python app.py
```

### Making Changes

1. **Editing Rules** - Modify `seattle_phase1_rules.json` (restart server to apply)
2. **Editing Templates** - Modify files in `templates/` (refresh browser to see changes)
3. **Editing Backend Logic** - Modify `app.py` or `engine.py` (restart server to apply)

### Testing Changes

```bash
# Stop server: CTRL+C
# Save your changes
# Restart server
python app.py

# Test in browser at http://127.0.0.1:5000
```

### Generating requirements.txt (if adding new packages)

```bash
pip freeze > requirements.txt
```

### Ending Work Session

```bash
# Stop server: CTRL+C
# Deactivate virtual environment
deactivate
```

---

## How It Works

### 1. User Input
The form collects key information:
- Zoning family (NR, RSL, Lowrise, etc.)
- ADU plan type (Attached, Detached, Both)
- Lot size and proposed ADU size
- Parking and sewer acknowledgements

### 2. Rules Evaluation
The engine (`engine.py`) evaluates inputs against rules in `seattle_phase1_rules.json`:
- **Blocker rules** → Automatic "UNLIKELY"
- **Warning rules** → Score reduction
- **Info rules** → Context with no score impact

### 3. Decision Output
Based on the final score and triggered rules:
- **LIKELY** (score ≥ 75): Few or no concerns
- **POSSIBLE** (40 ≤ score < 75): Some warnings or unknowns
- **UNLIKELY** (score < 40 or blockers): Major concerns

The results page shows:
- Final decision (Likely/Possible/Unlikely)
- Plain-English reasons for the decision
- Recommended next steps

---

## Editing Rules (No Code Changes Required)

All business logic lives in **`seattle_phase1_rules.json`**.

### Example Rule Structure

```json
{
  "id": "NR-DADU-MIN-LOT-3200",
  "severity": "blocker",
  "score_impact": -60,
  "when": {
    "all": [
      { "field": "zone_family", "op": "eq", "value": "NR" },
      { "field": "adu_plan", "op": "in", "value": ["DADU", "BOTH"] },
      { "field": "lot_size_sqft", "op": "lt", "value": 3200 }
    ]
  },
  "message": "For a detached ADU in NR zones, Seattle requires a 3,200 sq ft minimum lot size.",
  "next_steps": ["Verify lot size from property records"]
}
```

### Supported Operators

- `eq`, `neq` - Equality checks
- `gt`, `lt`, `gte`, `lte` - Numeric comparisons
- `in` - Value in list
- `is_null` - Check if field is empty/null

### Condition Logic

- `all` - AND logic (all conditions must be true)
- `any` - OR logic (any condition can be true)
- `always: true` - Always triggers

---

## Input Validation

Both **client-side** (JavaScript) and **server-side** (Python) validation enforce:

- Required fields: `zone_family`, `adu_plan`, `removing_required_parking`, `ack_sewer_capacity_charge`
- Allowed values for all dropdowns (exact match to spec)
- Numeric limits:
  - `lot_size_sqft`: 0-1,000,000
  - `proposed_adu_sqft`: 0-5,000
- Integer-only values for numeric fields

---

## Form Fields Reference

| Field                        | Type     | Values                                           | Required |
|------------------------------|----------|--------------------------------------------------|----------|
| `zone_family`                | Dropdown | NR, RSL, LOWRISE, OTHER, UNKNOWN                 | ✅       |
| `zone_detail`                | Dropdown | NR1, NR2, NR3, RSL, LOWRISE, UNKNOWN, or empty   | ❌       |
| `adu_plan`                   | Dropdown | AADU, DADU, BOTH, UNSURE                         | ✅       |
| `lot_size_sqft`              | Number   | 0-1,000,000 or empty                             | ❌       |
| `proposed_adu_sqft`          | Number   | 0-5,000 or empty                                 | ❌       |
| `existing_adus`              | Dropdown | 0, 1, 2, or empty                                | ❌       |
| `adding_second_adu`          | Dropdown | true, false, or empty                            | ❌       |
| `second_adu_criteria`        | Dropdown | GREEN, AFFORDABLE, UNKNOWN, NONE, or empty       | ❌       |
| `removing_required_parking`  | Dropdown | YES, NO, UNKNOWN                                 | ✅       |
| `ack_sewer_capacity_charge`  | Dropdown | YES, NO, UNKNOWN                                 | ✅       |

---

## Known Limitations (By Design)

- **No GIS or parcel lookup** - Relies on user-reported data
- **No database** - Rules are read from JSON at startup
- **Seattle only** - Not structured for multi-city support
- **Informational only** - Not a permit guarantee

---

## Troubleshooting

### Issue: `python: command not found` or `python3: command not found`

**Cause:** Python is not installed or not in system PATH

**Solution:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. During installation, check **"Add Python to PATH"** (Windows)
3. Restart your terminal/command prompt
4. Verify: `python --version`

---

### Issue: `git: command not found`

**Cause:** Git is not installed

**Solution:**
- **Windows:** Download from [git-scm.com](https://git-scm.com/downloads)
- **macOS:** `brew install git` or install Xcode Command Line Tools
- **Linux:** `sudo apt-get install git`

**Alternative:** Download the project as ZIP instead of using `git clone`

---

### Issue: Cannot activate virtual environment

**Windows Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then retry: `venv\Scripts\activate`

**macOS/Linux Error:** Permission denied

**Solution:**
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

---

### Issue: `ModuleNotFoundError: No module named 'flask'`

**Cause:** Flask not installed or virtual environment not activated

**Solution:**
1. Ensure virtual environment is activated (look for `(venv)` prefix)
2. Install Flask: `pip install flask`
3. Verify installation: `pip list | grep Flask`

---

### Issue: `Address already in use` / Port 5000 already in use

**Cause:** Another application is using port 5000

**Solution:**

**Option 1 - Use different port:**
```bash
# Open app.py and change the last line to:
app.run(debug=True, port=5001)
```

**Option 2 - Kill process on port 5000:**

Windows:
```bash
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

macOS/Linux:
```bash
lsof -ti:5000 | xargs kill -9
```

---

### Issue: `CRITICAL - Invalid JSON format in rules file`

**Cause:** JSON syntax error in `seattle_phase1_rules.json`

**Solution:**
1. Validate JSON at [jsonlint.com](https://jsonlint.com/)
2. Ensure file uses UTF-8 encoding
3. Check for missing commas, brackets, or quotes
4. Restore from Git if corrupted: `git checkout phase1-mvp -- seattle_phase1_rules.json`

---

### Issue: Page shows 404 Not Found

**Cause:** Template files missing or server not running

**Solution:**
1. Verify server is running (`python app.py`)
2. Check terminal for errors
3. Confirm `templates/` folder exists with `form.html` and `result.html`
4. Navigate to exactly: `http://127.0.0.1:5000` (not https)

---

### Issue: Form validation not working

**Cause:** JavaScript disabled or browser compatibility

**Solution:**
1. Enable JavaScript in browser settings
2. Use modern browser (Chrome, Firefox, Edge, Safari)
3. Clear browser cache (Ctrl+Shift+Delete)
4. Server-side validation still works even if JS is disabled

---

### Issue: Special characters display incorrectly (â€™ instead of ')

**Cause:** Encoding issue (already fixed in current version)

**Solution:** Update to latest version from `phase1-mvp` branch:
```bash
git pull origin phase1-mvp
```

The app automatically handles UTF-8-BOM encoding.

---

### Issue: Virtual environment folder is huge

**Cause:** Normal behavior - venv contains full Python environment

**Note:** The `venv/` folder should be:
- **Not committed to Git** (already in `.gitignore`)
- Approximately 10-50 MB depending on OS
- Can be deleted and recreated anytime with `python -m venv venv`

---

### Still Having Issues?

1. **Check terminal output** for specific error messages
2. **Verify project structure** matches the structure shown above
3. **Ensure all files are present** from the GitHub repository
4. **Try creating a fresh virtual environment:**
   ```bash
   deactivate  # if currently activated
   rm -rf venv  # or delete venv folder manually
   python -m venv venv
   venv\Scripts\activate
   pip install flask
   python app.py
   ```

---

## Next Steps for Users

After receiving results, users should:

1. **Review Seattle SDCI ADU guidance** at [seattle.gov/sdci](https://seattle.gov/sdci)
2. **Verify zoning** using Seattle's official zoning map
3. **Consult a qualified professional** (architect, permit expediter, or attorney)
4. **Request a pre-application conference** with SDCI if pursuing the project

---

## License & Disclaimer

This is an MVP demonstration tool. It provides general information only and does not constitute:
- Legal advice
- Permit approval or determination
- Professional consultation
- Guarantee of project feasibility

Always verify project details with the Seattle Department of Construction and Inspections (SDCI) and qualified professionals before proceeding with construction.

---

