@echo off
echo 🚀 ProctoFlex AI - Démarrage Complet
echo ====================================
echo.

echo 📋 Vérification des prérequis...
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé
    echo 💡 Installez Python depuis https://python.org/
    pause
    exit /b 1
)
echo ✅ Python détecté

REM Vérifier Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installé
    echo 💡 Installez Node.js depuis https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js détecté

echo.
echo 🎯 Démarrage des services...
echo.

echo 1️⃣ Démarrage du Backend...
start "ProctoFlex Backend" cmd /k "cd backend && python start_simple.py"

echo ⏳ Attente du démarrage du backend...
timeout /t 5 /nobreak >nul

echo 2️⃣ Démarrage de l'Application Desktop...
start "ProctoFlex Desktop" cmd /k "cd desktop && npm run dev"

echo.
echo ✅ Services démarrés !
echo.
echo 🌐 Accès aux applications :
echo    • Backend API: http://localhost:8000
echo    • Documentation API: http://localhost:8000/docs
echo    • Application Desktop: Se lance automatiquement
echo.
echo 💡 Pour arrêter les services, fermez les fenêtres de commande
echo.

pause
