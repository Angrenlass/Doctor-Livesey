@echo off
title Doctor Livesey Bot

echo === Doctor Livesey bot launcher ===

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Install Python 3.11+
    pause
    exit /b
)

REM Create venv if not exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Install requirements
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Run bot
echo Starting bot...
python main.py

pause