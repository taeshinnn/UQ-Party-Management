@echo off
echo 🎮 UQ Party Queue Manager - Quick Start
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found
echo.

if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
    echo.
)

echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📥 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🚀 Starting server...
echo.

python server.py --log=mock_game.log

pause

