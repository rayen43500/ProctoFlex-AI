@echo off
echo ========================================
echo   TEST DES STYLES ELECTRON DESKTOP
echo ========================================
echo.

echo [1/4] Verification des fichiers CSS...
if exist "src\renderer\styles\globals.css" (
    echo ✓ globals.css trouve
) else (
    echo ✗ globals.css manquant
)

if exist "src\renderer\styles\design-system.css" (
    echo ✓ design-system.css trouve
) else (
    echo ✗ design-system.css manquant
)

if exist "src\renderer\styles\electron-specific.css" (
    echo ✓ electron-specific.css trouve
) else (
    echo ✗ electron-specific.css manquant
)

echo.
echo [2/4] Verification de la configuration Tailwind...
if exist "tailwind.config.js" (
    echo ✓ tailwind.config.js trouve
) else (
    echo ✗ tailwind.config.js manquant
)

echo.
echo [3/4] Verification des dependances...
if exist "node_modules" (
    echo ✓ node_modules trouve
) else (
    echo ✗ node_modules manquant - Executez: npm install
)

echo.
echo [4/4] Verification des fichiers de build...
if exist "dist" (
    echo ✓ dossier dist trouve
) else (
    echo ! dossier dist manquant - Executez: npm run build
)

echo.
echo ========================================
echo   RESUME DU TEST
echo ========================================
echo.
echo Pour tester l'application:
echo 1. npm install (si pas fait)
echo 2. npm run dev
echo 3. Ouvrir l'application Electron
echo.
echo Les styles ont ete ameliores avec:
echo - Design system moderne
echo - Styles specifiques Electron
echo - Animations optimisees
echo - Responsive design
echo - Theme sombre support
echo.
pause
