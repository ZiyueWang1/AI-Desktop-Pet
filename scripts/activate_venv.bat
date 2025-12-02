@echo off
REM Quick activation script for Windows

if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Please run: scripts\setup_venv.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo ✅ Virtual environment activated!
echo You can now run: python run.py

