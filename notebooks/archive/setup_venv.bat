@echo off
echo ==========================================
echo Setting up Python Virtual Environment
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
if exist .venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Step 2: Activating virtual environment...
call .venv\Scripts\activate.bat

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip --quiet

echo Step 4: Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo To activate the virtual environment in the future, run:
echo   .venv\Scripts\activate.bat
echo.
echo To use in Jupyter Notebook:
echo   1. Activate the environment: .venv\Scripts\activate.bat
echo   2. Install ipykernel: pip install ipykernel
echo   3. Register kernel: python -m ipykernel install --user --name=.venv --display-name "Python (.venv)"
echo.
pause
