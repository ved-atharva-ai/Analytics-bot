@echo off
SETLOCAL EnableDelayedExpansion

TITLE AnalyticBot Launcher

echo ===================================================
echo      AnalyticBot Windows Installer & Launcher
echo ===================================================

REM 1. Check Prerequisites
echo.
echo [1/5] Checking prerequisites...

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.12+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in your PATH.
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM 2. Setup Python Virtual Environment
echo.
echo [2/5] Setting up Python environment...

IF NOT EXIST "venv" (
    echo Creating virtual environment 'venv'...
    python -m venv venv
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo Virtual environment 'venv' already exists.
)

REM Activate venv
call venv\Scripts\activate
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM 3. Install Backend Dependencies
echo.
echo [3/5] Installing backend dependencies...
pip install -r backend\requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b 1
)

REM 4. Install Frontend Dependencies
echo.
echo [4/5] Installing frontend dependencies...
cd frontend
call npm install
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install frontend dependencies.
    cd ..
    pause
    exit /b 1
)
cd ..

REM 5. Start Servers
echo.
echo [5/5] Starting servers...

echo Starting Backend (FastAPI) in a new window...
start "AnalyticBot Backend" cmd /k "call venv\Scripts\activate && python backend\main.py"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo Starting Frontend (Vite) in a new window...
cd frontend
start "AnalyticBot Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ===================================================
echo             AnalyticBot is running!
echo ===================================================
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:5173
echo.
echo Close the popup windows to stop the servers.
echo.
pause
