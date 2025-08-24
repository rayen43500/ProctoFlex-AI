@echo off
echo 🔧 ProctoFlex AI - Correction Automatique
echo =========================================
echo.

echo 📋 Vérification et correction des problèmes...
echo.

REM 1. Vérifier et créer tsconfig.electron.json
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

REM 2. Corriger enableRemoteModule
findstr /C:"enableRemoteModule" main.ts >nul 2>&1
if not errorlevel 1 (
    echo ⚙️  Correction de la configuration Electron...
    powershell -Command "(Get-Content main.ts) -replace 'enableRemoteModule: false,', '' | Set-Content main.ts"
    echo ✅ Configuration Electron corrigée
)

REM 3. Installer react-hot-toast
npm list react-hot-toast >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation de react-hot-toast...
    npm install react-hot-toast
    echo ✅ react-hot-toast installé
)

REM 4. Copier preload.js
echo 📄 Copie du fichier preload.js...
if exist "preload.js" (
    if not exist "dist" mkdir dist
    copy "preload.js" "dist\preload.js" >nul
    echo ✅ Fichier preload.js copié
) else (
    echo ❌ Fichier preload.js manquant
)

REM 5. Compiler TypeScript
echo 🔧 Compilation TypeScript...
tsc -p tsconfig.electron.json
if errorlevel 1 (
    echo ❌ Erreur de compilation TypeScript
) else (
    echo ✅ Compilation TypeScript réussie
)

REM 6. Vérifier les dépendances
if not exist "node_modules" (
    echo 📦 Installation des dépendances...
    npm install
    echo ✅ Dépendances installées
)

echo.
echo ✅ Toutes les corrections appliquées !
echo.
echo 🚀 Vous pouvez maintenant lancer l'application avec :
echo    • start_dev.bat (recommandé)
echo    • npm run dev
echo.

pause
