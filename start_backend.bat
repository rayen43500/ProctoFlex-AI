@echo off
echo ========================================
echo    ProctoFlex AI - Backend Startup
echo ========================================
echo.

cd backend

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo [3/4] Activating virtual environment...
call venv\Scripts\activate

echo.
echo [4/4] Installing dependencies...
pip install --upgrade pip
pip install -r requirements-simple.txt

echo.
echo [5/5] Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python main_simple.py

pause
