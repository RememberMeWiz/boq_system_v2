@echo off
title Plan2Takeoff V2 — Shutdown
echo ===================================================================
echo           PLAN2TAKEOFF V2 — SYSTEM SHUTDOWN SCRIPT
echo ===================================================================
echo.

echo Stopping Python backend processes (Port 5000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /f /pid %%a 2>nul
)

echo Stopping Node/Vite frontend processes (Port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173') do (
    taskkill /f /pid %%a 2>nul
)

echo.
echo ===================================================================
echo   All Plan2Takeoff V2 servers have been stopped.
echo ===================================================================
echo.
pause
