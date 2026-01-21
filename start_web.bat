@echo off
REM Blockchain Mining Simulation - Web Interface Startup Script (Windows)

echo ======================================
echo Blockchain Mining Simulation
echo Web Interface Startup
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import flask, flask_cors, matplotlib, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo √ Dependencies satisfied
echo.

REM Start the Flask application
echo Starting Flask server...
echo The web interface will be available at:
echo.
echo     http://localhost:5001
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

