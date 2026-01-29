@echo off
title ScalpMaster Bot
:loop
cls
echo ====================================================
echo             ScalpMaster Runtime (Windows)
echo ====================================================
echo Starting bot at %TIME%...
echo.

:: Ensure this path points to your actual python executable in venv
:: If invoking from root where venv is:
call venv\Scripts\activate.bat
python main.py

echo.
echo ====================================================
echo [WARNING] Bot crashed or stopped!
echo Restarting in 5 seconds...
echo Press Ctrl+C to terminate fully.
echo ====================================================
timeout /t 5 >nul
goto loop
