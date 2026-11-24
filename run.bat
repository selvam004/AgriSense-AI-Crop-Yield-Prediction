@echo off
TITLE AgriSense - Django Server Launcher
echo ========================================================
echo   Starting AgriSense - AI Crop Yield Prediction (Django)
echo ========================================================
echo.

:: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [*] Creating virtual environment (venv)...
    python -m venv venv
)

:: Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo [*] Installing required packages...
pip install -r requirements.txt --quiet

:: Run database migrations
echo [*] Checking database migrations...
python manage.py migrate --noinput

echo.
echo ========================================================
echo   AgriSense is ready!
echo   * Main Dashboard: http://127.0.0.1:8000/
echo   * Admin Portal:   http://127.0.0.1:8000/admin/
echo   * Admin User:     admin
echo   * Admin Password: admin123
echo ========================================================
echo.
echo Press Ctrl+C in this window to stop the server.
echo.

python manage.py runserver 127.0.0.1:8000
pause
