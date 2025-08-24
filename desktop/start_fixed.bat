@echo off
echo Démarrage de ProctoFlex AI Desktop...

REM Nettoyer le dossier dist
if exist dist rmdir /s /q dist

REM Compiler TypeScript
echo Compilation TypeScript...
npx tsc -p tsconfig.electron.json

REM Copier preload.js
echo Copie du preload script...
copy preload.js dist\preload.js

REM Démarrer Vite en arrière-plan
echo Démarrage du serveur Vite...
start /B npm run dev:renderer

REM Attendre que Vite soit prêt
echo Attente du serveur Vite...
timeout /t 5 /nobreak > nul

REM Démarrer Electron avec les bonnes variables
echo Démarrage d'Electron...
set NODE_ENV=development
set ELECTRON_IS_DEV=1
set DEBUG=electron:*
electron .

pause
