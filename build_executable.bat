@echo off
echo ================================
echo   Building Countdown Pro EXE
echo ================================
echo.

:: Check if in correct directory
if not exist "enhanced_countdown_app.py" (
    echo Error: enhanced_countdown_app.py not found!
    echo Please run this from the project directory.
    pause
    exit /b 1
)

:: Install required packages
echo Installing required packages...
pip install pyinstaller

echo.
echo Building executable...
echo.

:: Build the executable with enhanced options
"C:\all projects\countdown desktop widget\.venv\Scripts\pyinstaller.exe" ^
    --onefile ^
    --windowed ^
    --name "CountdownPro" ^
    --add-data "*.py;." ^
    --hidden-import "plyer" ^
    --hidden-import "plyer.platforms.win" ^
    --hidden-import "plyer.platforms.win.notification" ^
    --hidden-import "pystray" ^
    --hidden-import "pystray._win32" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "sqlite3" ^
    --hidden-import "customtkinter" ^
    --exclude-module "tkinter.test" ^
    enhanced_countdown_app.py

echo.
if exist "dist\CountdownPro.exe" (
    echo ================================
    echo   BUILD SUCCESSFUL! 🎉
    echo ================================
    echo.
    echo Your executable is ready:
    echo 📁 Location: %CD%\dist\CountdownPro.exe
    echo.
    echo You can now:
    echo 1. Run the EXE directly from dist folder
    echo 2. Copy it to your Desktop
    echo 3. Pin it to taskbar
    echo 4. Add to startup folder for auto-start
    echo.
) else (
    echo ================================
    echo   BUILD FAILED! ❌
    echo ================================
    echo Check the error messages above.
)

pause
