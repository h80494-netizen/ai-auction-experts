@echo off
cd /d "%~dp0"
echo =========================================
echo AI Auction Analyst - Start Script
echo =========================================
echo.
echo Starting FastAPI Backend Server...
cd backend
start "AI Auction Backend" cmd /k "C:\Users\llll\AppData\Local\Programs\Python\Python312\python.exe app.py"

echo Waiting for backend to initialize (3 seconds)...
timeout /t 3 /nobreak > NUL

echo Opening Frontend Dashboard...
cd ..
start http://localhost:8001

echo.
echo Backend is running in a separate window.
echo You can now use the dashboard in your browser!
echo =========================================
