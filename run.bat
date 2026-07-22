@echo off
title Plan2Takeoff V2 Launcher
set PYTHONIOENCODING=utf-8
echo ========================================================
echo        Plan2Takeoff V2 Structural Engine Launcher
echo ========================================================
echo.
echo Starting Flask API Backend and Dashboard on http://127.0.0.1:5001 ...
python backend/app.py
pause
