@echo off
echo Starting Frontend Development Server...
echo.

cd frontend

echo Cleaning cache...
if exist dist rmdir /s /q dist
if exist node_modules\.vite rmdir /s /q node_modules\.vite

echo Installing dependencies...
call npm install

echo Starting development server...
call npm run dev

pause
