# PowerShell script to set up Python Virtual Environment
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setting up Python Virtual Environment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://www.python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 1: Create virtual environment
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path .venv) {
    Write-Host "Virtual environment already exists. Removing old one..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Activate virtual environment
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Step 3: Upgrade pip
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Step 4: Install packages
Write-Host "Step 4: Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install packages" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 5: Install ipykernel for Jupyter
Write-Host "Step 5: Installing ipykernel for Jupyter Notebook..." -ForegroundColor Yellow
pip install ipykernel
python -m ipykernel install --user --name=.venv --display-name "Python (.venv)"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment in the future, run:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "The Jupyter kernel has been registered." -ForegroundColor Cyan
Write-Host "Select 'Python (.venv)' as your kernel in Jupyter Notebook." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
