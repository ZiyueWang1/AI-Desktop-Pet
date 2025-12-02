@echo off
REM Virtual environment setup script for Windows

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ✅ Virtual environment setup complete!
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate
echo.
echo To deactivate, run:
echo   deactivate

pause

