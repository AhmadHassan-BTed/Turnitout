@echo off
setlocal enabledelayedexpansion

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Turnitout] Python is not detected on your system.
    echo [Turnitout] Attempting to install Python automatically via winget...
    
    :: Verify winget is available
    winget --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [Turnitout] ERROR: winget is not available. Please install Python manually from https://python.org.
        pause
        exit /b 1
    )
    
    echo [Turnitout] Installing Python 3. Please accept any system prompts...
    winget install -e --id Python.Python.3 --accept-source-agreements --accept-package-agreements
    
    if %errorlevel% neq 0 (
        echo [Turnitout] Installation failed or was cancelled. Please install Python manually.
        pause
        exit /b 1
    )
    
    echo [Turnitout] Python installed successfully! Please restart this command window and run again.
    pause
    exit /b 0
)

:: Python is present, check if package dependencies are installed
python -c "import dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Turnitout] Initializing package dependencies in the background...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -e . >nul 2>&1
)

:: Run the script
python run.py %*
pause
