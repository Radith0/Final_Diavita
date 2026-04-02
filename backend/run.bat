@echo off
REM Diabetes Detection AI Backend - Quick Start Script

echo Starting Diabetes Detection AI Backend...

REM Kill any existing process on port 5000
echo Checking for existing processes on port 5000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    echo Killing process %%a on port 5000...
    taskkill /F /PID %%a >nul 2>&1
    timeout /t 1 /nobreak >nul
    echo Port 5000 cleared.
    goto port_cleared
)
echo Port 5000 is available.
:port_cleared

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "models\retinal\weights" mkdir models\retinal\weights
if not exist "models\lifestyle\weights" mkdir models\lifestyle\weights

REM Run the application
echo Starting Flask server...
python app.py