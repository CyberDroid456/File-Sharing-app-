@echo off
echo ===============================
echo  File Share App + Ngrok Launcher
echo ===============================
echo.

echo 🚀 Starting Python Flask server...
echo 📍 Look at the NEW WINDOW for server messages!
start "Flask Server" python app.py

echo ⏳ Waiting 5 seconds for server to start...
timeout /t 5 /nobreak >nul

echo 🌐 Starting ngrok tunnel...
echo.
echo ===== ACCESS URLs =====
echo 📍 Local: http://127.0.0.1:5000
echo 🌍 Public: Check ngrok output below
echo =======================
echo.
echo Press Ctrl+C to stop ngrok (keep Flask window open)
echo.

ngrok http 5000

echo.
echo 🌐 Ngrok stopped!
echo 📋 Flask server is still running in other window
echo ✅ Ngrok terminated successfully
pause