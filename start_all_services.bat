@echo off
echo ========================================
echo Starting All ProctoFlex Services
echo ========================================
echo.

echo Starting Backend Server...
start "Backend" cmd /k "cd backend && python main_simple.py"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend Development Server...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo Waiting 3 seconds for frontend to start...
timeout /t 3 /nobreak > nul

echo Starting Desktop Application...
start "Desktop" cmd /k "cd desktop && npm run dev"

echo.
echo ========================================
echo All services are starting...
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Desktop: Electron app
echo.
echo Press any key to close this window...
pause > nul
