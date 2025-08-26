@echo off
echo ========================================
echo    ProctoFlex AI - Complete Startup
echo ========================================
echo.

echo [1/4] Starting Backend...
start "ProctoFlex Backend" cmd /k "cd backend && python -m venv venv && call venv\Scripts\activate && pip install -r requirements-simple.txt && python main_simple.py"

echo.
echo [2/4] Waiting for backend to start...
timeout /t 10 /nobreak > nul

echo.
echo [3/4] Starting Desktop Application...
start "ProctoFlex Desktop" cmd /k "cd desktop && npm install && npm run dev"

echo.
echo [4/4] Opening web interfaces...
timeout /t 5 /nobreak > nul
start http://localhost:8000/docs
start http://localhost:3000

echo.
echo ========================================
echo    ProctoFlex AI Started Successfully!
echo ========================================
echo.
echo Services available at:
echo - Backend API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - Frontend Admin: http://localhost:3000
echo - Desktop App: Running in Electron window
echo.
echo Press any key to exit...
pause > nul
