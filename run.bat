@echo off
title File Share Application
echo ========================================
echo    File Share Application Launcher
echo ========================================
echo.
echo Starting server...
echo.
echo Once started, open your web browser and go to:
echo http://localhost:5000
echo.
echo Default login credentials:
echo Admin: admin/admin123
echo User: user/user123
echo.
echo Press Ctrl+C to stop the server
echo.
echo Note: You can edit config.py to customize:
echo - Maximum file size (currently 1000MB)
echo - Allowed file types
echo - User accounts and passwords
echo - Server settings
echo.
python app.py
pause