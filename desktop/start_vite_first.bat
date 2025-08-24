@echo off
echo 🚀 ProctoFlex AI - Démarrage Vite First
echo =======================================
echo.

echo 📋 Vérification des prérequis...
echo.

REM Vérifier Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installé
    pause
    exit /b 1
)
echo ✅ Node.js détecté

REM Vérifier les dépendances
if not exist "node_modules" (
    echo 📦 Installation des dépendances...
    npm install
)

REM Copier preload.js
echo 📄 Copie du fichier preload.js...
if exist "preload.js" (
    if not exist "dist" mkdir dist
    copy "preload.js" "dist\preload.js" >nul
    echo ✅ Fichier preload.js copié
)

REM Compiler TypeScript
echo 🔧 Compilation TypeScript...
npx tsc -p tsconfig.electron.json
if errorlevel 1 (
    echo ❌ Erreur de compilation TypeScript
    pause
    exit /b 1
)
echo ✅ Compilation TypeScript réussie

echo.
echo 🎯 Démarrage du serveur Vite...
echo.

REM Démarrer Vite en arrière-plan
start "Vite Server" cmd /k "npm run dev:renderer"

echo ⏳ Attente du serveur Vite (10 secondes)...
timeout /t 10 /nobreak >nul

echo 🔍 Test de connexion au serveur Vite...
curl -s http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Le serveur Vite n'est pas encore prêt
    echo 💡 Attente supplémentaire...
    timeout /t 5 /nobreak >nul
) else (
    echo ✅ Serveur Vite prêt sur http://localhost:5173
)

echo.
echo 🖥️  Démarrage d'Electron...
echo.

REM Démarrer Electron
set NODE_ENV=development
npm run dev:main

pause
