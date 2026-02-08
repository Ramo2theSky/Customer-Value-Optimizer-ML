# Quick Start Guide - Fix Virtual Environment Loading Issue

## Problem
The virtual environment is loading too slowly or not working properly.

## Solution

### Step 1: Run the Setup Script

**For PowerShell (Recommended):**
```powershell
.\setup_venv.ps1
```

**For Command Prompt:**
```cmd
setup_venv.bat
```

This script will:
- Create a fresh virtual environment (`.venv`)
- Install all required packages
- Register the Jupyter kernel automatically

### Step 2: Select the Correct Kernel in Jupyter

1. Open your notebook in Jupyter/VS Code
2. Click on the kernel selector (top right)
3. Select **"Python (.venv)"** as your kernel
4. If you don't see it, restart Jupyter/VS Code after running the setup script

### Step 3: Place Your Data File

Make sure your Excel file `SPE-OPT-31122025.xlsx` is in the same folder as the notebook, or update the path in the notebook.

## Manual Setup (If Scripts Don't Work)

1. **Create virtual environment:**
   ```powershell
   python -m venv .venv
   ```

2. **Activate it:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install packages:**
   ```powershell
   pip install -r requirements.txt
   pip install ipykernel
   ```

4. **Register kernel:**
   ```powershell
   python -m ipykernel install --user --name=.venv --display-name "Python (.venv)"
   ```

## Why It Was Slow

The virtual environment was likely:
- Missing required packages (causing import errors)
- Not properly registered as a Jupyter kernel
- Trying to install packages on-the-fly (very slow)
- Using incorrect Python paths

## Fixed Issues

✅ Created `requirements.txt` with all dependencies
✅ Fixed file paths (changed from Colab paths to local paths)
✅ Created automated setup scripts
✅ Notebooks now use relative paths

## Next Steps

1. Run `setup_venv.ps1` or `setup_venv.bat`
2. Select "Python (.venv)" kernel in your notebook
3. Run your code!
