@echo off
title Media Downloader
cd /d "%~dp0"

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create venv if missing
if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Install / update dependencies
echo [*] Checking dependencies...
.venv\Scripts\pip.exe install -q -r requirements.txt

:: Launch the app
echo [*] Starting Media Downloader...
.venv\Scripts\python.exe main.py
