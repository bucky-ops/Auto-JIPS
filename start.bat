@echo off
echo ========================================
echo AJIPS - Quick Start Script
echo ========================================
echo.

echo [1/4] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Running tests...
pytest tests/test_core_functionality.py -v
if errorlevel 1 (
    echo Warning: Some tests failed, but continuing...
)

echo.
echo [4/4] Starting AJIPS server...
echo.
echo ========================================
echo AJIPS is starting!
echo ========================================
echo.
echo Web UI: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Health Check: http://127.0.0.1:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uvicorn ajips.app.main:app --reload
