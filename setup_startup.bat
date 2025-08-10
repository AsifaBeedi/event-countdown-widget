@echo off
echo ================================
echo   Countdown Pro - Startup Setup
echo ================================
echo.

set APP_NAME=CountdownPro
set CURRENT_DIR=%~dp0
set PYTHON_SCRIPT=%CURRENT_DIR%enhanced_countdown_app.py
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo Setting up Countdown Pro to start with Windows...
echo.

:: Create startup batch file
echo @echo off > "%STARTUP_FOLDER%\%APP_NAME%.bat"
echo cd /d "%CURRENT_DIR%" >> "%STARTUP_FOLDER%\%APP_NAME%.bat"
echo python "%PYTHON_SCRIPT%" >> "%STARTUP_FOLDER%\%APP_NAME%.bat"

echo ✅ Startup file created: %STARTUP_FOLDER%\%APP_NAME%.bat
echo.
echo Countdown Pro will now:
echo 🚀 Start automatically when Windows boots
echo 🔄 Run in system tray (background)
echo 📱 Show notifications for your events
echo ⚡ Be accessible via system tray icon
echo.
echo To disable auto-start:
echo 📁 Go to: %STARTUP_FOLDER%
echo 🗑️  Delete: %APP_NAME%.bat
echo.

pause
