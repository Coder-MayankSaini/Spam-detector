@echo off
echo =========================================
echo    Spam Detector Server - Windows
echo =========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo [INFO] Python detected
echo [INFO] Starting server with Windows optimizations...
echo.

REM Try to run with administrator privileges for firewall rules
echo [INFO] Attempting to add Windows Firewall exceptions...
echo [INFO] You may see a UAC prompt - click Yes to allow firewall configuration

REM Start the server
python start_server.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server failed to start
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure no other applications are using port 5001
    echo 2. Try running as Administrator
    echo 3. Check Windows Firewall settings
    echo 4. Verify antivirus isn't blocking Python
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [INFO] Server stopped successfully
pause
