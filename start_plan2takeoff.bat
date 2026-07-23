@echo off
title Plan2Takeoff V2 — Launcher
echo ===================================================================
echo           PLAN2TAKEOFF V2 — AUTOMATED SYSTEM LAUNCHER
echo ===================================================================
echo.

:: Launch Backend API Server in a new window
echo [1/3] Starting Backend API Engine on http://localhost:5000 ...
start "Plan2Takeoff V2 — Backend Engine (Port 5000)" powershell -NoExit -ExecutionPolicy Bypass -Command "cd '%~dp0backend'; python app.py"

:: Wait 3 seconds for backend initialization
timeout /t 3 /nobreak >nul

:: Launch Frontend Vite Dev Server in a new window
echo [2/3] Starting Frontend UI Server on http://localhost:5173 ...
start "Plan2Takeoff V2 — Frontend UI (Port 5173)" powershell -NoExit -ExecutionPolicy Bypass -Command "cd '%~dp0frontend'; node node_modules/vite/bin/vite.js"

:: Wait 3 seconds for Vite server initialization
timeout /t 3 /nobreak >nul

:: Open Default Browser
echo [3/3] Opening Web Dashboard in Browser...
start http://localhost:5173

echo.
echo ===================================================================
echo   SUCCESS: Plan2Takeoff V2 is now active!
echo   - Backend API:  http://localhost:5000
echo   - Frontend UI: http://localhost:5173
echo.
echo   (To stop the servers, simply close the opened PowerShell windows)
echo ===================================================================
echo.
pause
