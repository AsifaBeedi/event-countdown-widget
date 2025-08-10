@echo off
echo ================================
echo   Desktop Shortcut Creator
echo ================================
echo.

set SOURCE_EXE="c:\all projects\countdown desktop widget\dist\CountdownPro.exe"
set TARGET_NAME="CountdownPro.exe"

:: Try multiple possible desktop locations
set DESKTOP1="%USERPROFILE%\Desktop"
set DESKTOP2="%USERPROFILE%\OneDrive\Desktop"
set DESKTOP3="%PUBLIC%\Desktop"

if exist %DESKTOP1% (
    copy %SOURCE_EXE% %DESKTOP1%\%TARGET_NAME%
    echo ✅ Copied to Desktop: %DESKTOP1%\%TARGET_NAME%
    goto :success
)

if exist %DESKTOP2% (
    copy %SOURCE_EXE% %DESKTOP2%\%TARGET_NAME%
    echo ✅ Copied to OneDrive Desktop: %DESKTOP2%\%TARGET_NAME%
    goto :success
)

if exist %DESKTOP3% (
    copy %SOURCE_EXE% %DESKTOP3%\%TARGET_NAME%
    echo ✅ Copied to Public Desktop: %DESKTOP3%\%TARGET_NAME%
    goto :success
)

echo ❌ No desktop folder found. Manual steps:
echo 1. Navigate to: c:\all projects\countdown desktop widget\dist\
echo 2. Right-click CountdownPro.exe
echo 3. Select "Send to" → "Desktop (create shortcut)"
goto :end

:success
echo.
echo 🎉 SUCCESS! CountdownPro is now on your desktop!
echo.
echo You can now:
echo 📱 Double-click the desktop icon to launch
echo 📌 Right-click the desktop icon → "Pin to taskbar"
echo 🚀 Add to startup folder for auto-launch

:end
echo.
pause
