@echo off
setlocal
title ScalpMaster Auto-Updater

:check_git
echo [SYSTEM] Checking Git availability...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH!
    echo Please install Git for Windows: https://git-scm.com/download/win
    pause
    exit /b
)

:update
echo.
echo ====================================================
echo        ScalpMaster Auto-Updater (v1.2)
echo ====================================================
echo [GIT] Pulling latest changes...
git pull origin main
if %errorlevel% neq 0 (
    echo [WARNING] Git pull failed. Checking connection...
    echo Continuing with local version...
) else (
    echo [GIT] Successfully updated.
)

:dependencies
echo.
echo [PIP] Checking Python dependencies...
python -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements!
    echo Check your internet connection or Python path.
    pause
    exit /b
)
echo [PIP] Dependencies ready.

:run
echo.
echo ====================================================
echo             ScalpMaster Runtime
echo ====================================================
echo Starting bot at %TIME%...
echo.

python main.py

echo.
echo ====================================================
echo [WARNING] Bot crashed or stopped!
echo Restarting in 5 seconds...
echo Press Ctrl+C quickly to terminate.
echo ====================================================
timeout /t 5 >nul
goto run
