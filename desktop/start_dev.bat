@echo off
echo 🚀 ProctoFlex AI Desktop - Démarrage Développement Amélioré
echo ============================================================
echo.

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installé ou n'est pas dans le PATH
    echo 💡 Installez Node.js depuis https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js détecté

REM Vérifier si les dépendances sont installées
if not exist "node_modules" (
    echo 📦 Installation des dépendances...
    npm install
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

REM Vérifier et corriger les problèmes courants
echo 🔧 Vérification de la configuration...

REM Vérifier tsconfig.electron.json
if not exist "tsconfig.electron.json" (
    echo ⚙️  Création du fichier tsconfig.electron.json...
    echo {> tsconfig.electron.json
    echo   "compilerOptions": {>> tsconfig.electron.json
    echo     "target": "ES2020",>> tsconfig.electron.json
    echo     "module": "commonjs",>> tsconfig.electron.json
    echo     "lib": ["ES2020"],>> tsconfig.electron.json
    echo     "outDir": "dist",>> tsconfig.electron.json
    echo     "rootDir": ".",>> tsconfig.electron.json
    echo     "strict": true,>> tsconfig.electron.json
    echo     "esModuleInterop": true,>> tsconfig.electron.json
    echo     "skipLibCheck": true,>> tsconfig.electron.json
    echo     "forceConsistentCasingInFileNames": true,>> tsconfig.electron.json
    echo     "resolveJsonModule": true,>> tsconfig.electron.json
    echo     "allowSyntheticDefaultImports": true,>> tsconfig.electron.json
    echo     "moduleResolution": "node",>> tsconfig.electron.json
    echo     "declaration": false,>> tsconfig.electron.json
    echo     "sourceMap": true,>> tsconfig.electron.json
    echo     "removeComments": true,>> tsconfig.electron.json
    echo     "noImplicitAny": true,>> tsconfig.electron.json
    echo     "noImplicitReturns": true,>> tsconfig.electron.json
    echo     "noImplicitThis": true,>> tsconfig.electron.json
    echo     "noUnusedLocals": false,>> tsconfig.electron.json
    echo     "noUnusedParameters": false>> tsconfig.electron.json
    echo   },>> tsconfig.electron.json
    echo   "include": [>> tsconfig.electron.json
    echo     "main.ts",>> tsconfig.electron.json
    echo     "preload.js">> tsconfig.electron.json
    echo   ],>> tsconfig.electron.json
    echo   "exclude": [>> tsconfig.electron.json
    echo     "node_modules",>> tsconfig.electron.json
    echo     "dist",>> tsconfig.electron.json
    echo     "src/renderer">> tsconfig.electron.json
    echo   ]>> tsconfig.electron.json
    echo }>> tsconfig.electron.json
    echo ✅ Fichier tsconfig.electron.json créé
)

REM Corriger enableRemoteModule
findstr /C:"enableRemoteModule" main.ts >nul 2>&1
if not errorlevel 1 (
    echo ⚙️  Correction de la configuration Electron...
    powershell -Command "(Get-Content main.ts) -replace 'enableRemoteModule: false,', '' | Set-Content main.ts"
    echo ✅ Configuration Electron corrigée
)

REM Vérifier react-hot-toast
npm list react-hot-toast >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation de react-hot-toast...
    npm install react-hot-toast
)

echo.
echo 🎯 Démarrage en mode développement...
echo 💡 Le serveur Vite démarrera d'abord, puis Electron
echo.

REM Démarrer le serveur Vite en arrière-plan
echo 📡 Démarrage du serveur Vite...
start "Vite Dev Server" cmd /k "npm run dev:renderer"

REM Attendre que le serveur soit prêt
echo ⏳ Attente du serveur Vite...
timeout /t 3 /nobreak >nul

REM Démarrer Electron
echo 🖥️  Démarrage d'Electron...
set NODE_ENV=development
npm run dev:main

pause
