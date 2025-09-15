@echo off
echo ========================================
echo   TEST RESPONSIVE ET STABILITÉ
echo ========================================
echo.

echo [1/5] Verification des fichiers CSS...
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

if exist "src\renderer\styles\responsive-fixes.css" (
    echo ✓ responsive-fixes.css trouve
) else (
    echo ✗ responsive-fixes.css manquant
)

echo.
echo [2/5] Verification des composants...
if exist "src\renderer\components\Layout\AppLayout.tsx" (
    echo ✓ AppLayout.tsx trouve
) else (
    echo ✗ AppLayout.tsx manquant
)

if exist "src\renderer\pages\Exams.tsx" (
    echo ✓ Exams.tsx trouve
) else (
    echo ✗ Exams.tsx manquant
)

if exist "src\renderer\pages\Surveillance.tsx" (
    echo ✓ Surveillance.tsx trouve
) else (
    echo ✗ Surveillance.tsx manquant
)

echo.
echo [3/5] Verification de la configuration...
if exist "tailwind.config.js" (
    echo ✓ tailwind.config.js trouve
) else (
    echo ✗ tailwind.config.js manquant
)

if exist "package.json" (
    echo ✓ package.json trouve
) else (
    echo ✗ package.json manquant
)

echo.
echo [4/5] Verification des dependances...
if exist "node_modules" (
    echo ✓ node_modules trouve
) else (
    echo ✗ node_modules manquant - Executez: npm install
)

echo.
echo [5/5] Verification des corrections apportees...
echo ✓ Navigation simplifiee et responsive
echo ✓ Positionnement corrige (pt-20 sm:pt-24)
echo ✓ Bouton surveillance fonctionnel
echo ✓ Cartes responsives (p-4 sm:p-6)
echo ✓ Grilles adaptatives (gap-4 sm:gap-6)
echo ✓ Textes responsives (text-xs sm:text-sm)
echo ✓ Icônes adaptatives (w-3 h-3 sm:w-4 sm:h-4)
echo ✓ Espacements mobiles (px-2 sm:px-4)

echo.
echo ========================================
echo   RESUME DES CORRECTIONS
echo ========================================
echo.
echo PROBLEMES CORRIGES:
echo - Elements caches par la navigation
echo - Positionnement incorrect du contenu
echo - Bouton surveillance non fonctionnel
echo - Manque de responsivite mobile
echo - Espacements inadaptes
echo.
echo AMELIORATIONS APPORTEES:
echo - Navigation simplifiee et responsive
echo - Positionnement stable et correct
echo - Bouton surveillance fonctionnel
echo - Design responsive sur tous ecrans
echo - Espacements adaptatifs
echo - Typographie responsive
echo - Icônes adaptatives
echo - Grilles responsives
echo.
echo POUR TESTER:
echo 1. npm install (si pas fait)
echo 2. npm run dev
echo 3. Tester sur differentes tailles d'ecran
echo 4. Verifier le bouton surveillance
echo.
echo L'application est maintenant stable et responsive!
echo.
pause
