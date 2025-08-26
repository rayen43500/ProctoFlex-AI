@echo off
echo ========================================
echo    ProctoFlex AI - Desktop App
echo ========================================
echo.

cd desktop

echo [1/3] Installing dependencies...
if not exist "node_modules" (
    npm install
    echo Dependencies installed.
) else (
    echo Dependencies already installed.
)

echo.
echo [2/3] Starting development server...
echo Desktop app will start automatically...
echo.

npm run dev

pause
