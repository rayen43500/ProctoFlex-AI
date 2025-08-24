@echo off
echo 🚀 ProctoFlex AI - Démarrage du Backend
echo =======================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou n'est pas dans le PATH
    echo 💡 Installez Python depuis https://python.org/
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Aller dans le répertoire backend
cd backend

REM Vérifier si le répertoire backend existe
if not exist "main_simple.py" (
    echo ❌ Répertoire backend non trouvé ou fichiers manquants
    echo 💡 Assurez-vous d'être dans le bon répertoire
    pause
    exit /b 1
)

echo ✅ Répertoire backend trouvé

REM Vérifier si les dépendances sont installées
if not exist "requirements.txt" (
    echo ❌ Fichier requirements.txt manquant
    echo 💡 Exécutez d'abord l'installation
    pause
    exit /b 1
)

REM Vérifier si uvicorn est installé
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation des dépendances...
    python install_simple.py
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation des dépendances
        pause
        exit /b 1
    )
)

echo.
echo 🎯 Démarrage du serveur backend...
echo 💡 Le serveur sera accessible sur http://localhost:8000
echo.

python start_simple.py

pause
