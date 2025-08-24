#!/usr/bin/env python3
"""
Script d'installation spécifique pour Windows
Gère les erreurs et installe les dépendances étape par étape
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description, continue_on_error=False):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} réussi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} échoué")
        print(f"Erreur: {e.stderr}")
        if continue_on_error:
            print("⚠️  Continuation malgré l'erreur...")
            return False
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro} détecté")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ est requis")
        return False
    
    print("✅ Version Python compatible")
    return True

def install_core_dependencies():
    """Installe les dépendances de base essentielles"""
    print("\n📦 Installation des dépendances de base...")
    
    # Mettre à jour pip
    if not run_command("python -m pip install --upgrade pip", "Mise à jour de pip"):
        return False
    
    # Installer les dépendances une par une pour identifier les problèmes
    core_packages = [
        ("fastapi==0.104.1", "FastAPI"),
        ("uvicorn[standard]==0.24.0", "Uvicorn"),
        ("python-multipart==0.0.6", "Python-Multipart"),
        ("python-dotenv==1.0.0", "Python-Dotenv"),
        ("pydantic==2.5.0", "Pydantic"),
        ("pydantic-settings==2.1.0", "Pydantic-Settings"),
    ]
    
    for package, description in core_packages:
        if not run_command(f"pip install {package}", f"Installation de {description}"):
            print(f"⚠️  Échec de {description}, tentative de continuation...")
            continue
    
    return True

def install_database_dependencies():
    """Installe les dépendances de base de données"""
    print("\n🗄️  Installation des dépendances de base de données...")
    
    db_packages = [
        ("sqlalchemy==2.0.23", "SQLAlchemy"),
        ("psycopg2-binary==2.9.9", "PostgreSQL"),
        ("alembic==1.12.1", "Alembic"),
    ]
    
    for package, description in db_packages:
        if not run_command(f"pip install {package}", f"Installation de {description}"):
            print(f"⚠️  Échec de {description}, tentative de continuation...")
            continue
    
    return True

def install_security_dependencies():
    """Installe les dépendances de sécurité"""
    print("\n🔒 Installation des dépendances de sécurité...")
    
    security_packages = [
        ("python-jose[cryptography]==3.3.0", "Python-Jose"),
        ("passlib[bcrypt]==1.7.4", "Passlib"),
    ]
    
    for package, description in security_packages:
        if not run_command(f"pip install {package}", f"Installation de {description}"):
            print(f"⚠️  Échec de {description}, tentative de continuation...")
            continue
    
    return True

def install_ai_dependencies():
    """Installe les dépendances d'IA (Windows compatible)"""
    print("\n🤖 Installation des dépendances d'IA...")
    
    # Essayer d'abord les versions précompilées
    ai_packages = [
        ("numpy>=1.24.0", "NumPy"),
        ("pillow>=10.0.0", "Pillow"),
    ]
    
    for package, description in ai_packages:
        if not run_command(f"pip install {package}", f"Installation de {description}"):
            print(f"⚠️  Échec de {description}, tentative de continuation...")
            continue
    
    # OpenCV - essayer plusieurs versions
    opencv_versions = [
        "opencv-python-headless==4.8.1.78",
        "opencv-python-headless>=4.8.0",
        "opencv-python>=4.8.0",
    ]
    
    opencv_installed = False
    for opencv_package in opencv_versions:
        if run_command(f"pip install {opencv_package}", "Installation d'OpenCV"):
            opencv_installed = True
            break
    
    if not opencv_installed:
        print("⚠️  OpenCV n'a pas pu être installé, certaines fonctionnalités seront limitées")
    
    return True

def install_optional_dependencies():
    """Installe les dépendances optionnelles"""
    print("\n🎵 Installation des dépendances optionnelles...")
    
    optional_packages = [
        ("websockets==12.0", "WebSockets"),
        ("pytest==7.4.3", "Pytest"),
        ("pytest-asyncio==0.21.1", "Pytest-AsyncIO"),
    ]
    
    for package, description in optional_packages:
        if not run_command(f"pip install {package}", f"Installation de {description}"):
            print(f"⚠️  Échec de {description}, tentative de continuation...")
            continue
    
    return True

def create_env_file():
    """Crée le fichier .env"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Fichier .env existe déjà")
        return True
    
    print("\n🔧 Création du fichier .env...")
    env_content = """# Configuration de l'environnement ProctoFlex AI

# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/proctoflex
DATABASE_TEST_URL=postgresql://user:password@localhost:5432/proctoflex_test

# Sécurité
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Serveur
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# IA et Computer Vision
FACE_RECOGNITION_TOLERANCE=0.6
MIN_FACE_CONFIDENCE=0.8

# Stockage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Redis (optionnel)
REDIS_URL=redis://localhost:6379

# Monitoring
ENABLE_METRICS=true
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Fichier .env créé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env: {e}")
        return False

def create_directories():
    """Crée les répertoires nécessaires"""
    print("\n📁 Création des répertoires...")
    
    directories = [
        "logs",
        "uploads",
        "uploads/images",
        "uploads/videos",
        "uploads/audio",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire {directory} créé")
    
    return True

def main():
    """Fonction principale"""
    print("🚀 Installation Windows de ProctoFlex AI Backend")
    print("=" * 60)
    
    # Vérifier la version de Python
    if not check_python_version():
        sys.exit(1)
    
    # Installation étape par étape
    steps = [
        ("Dépendances de base", install_core_dependencies),
        ("Dépendances de base de données", install_database_dependencies),
        ("Dépendances de sécurité", install_security_dependencies),
        ("Dépendances d'IA", install_ai_dependencies),
        ("Dépendances optionnelles", install_optional_dependencies),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_function():
            failed_steps.append(step_name)
            print(f"⚠️  {step_name} a échoué partiellement")
    
    # Créer la configuration
    print(f"\n{'='*20} Configuration {'='*20}")
    create_env_file()
    create_directories()
    
    # Résumé
    print(f"\n{'='*20} Résumé de l'installation {'='*20}")
    if failed_steps:
        print(f"⚠️  Étapes avec des problèmes: {', '.join(failed_steps)}")
        print("💡 Certaines fonctionnalités peuvent être limitées")
    else:
        print("🎉 Toutes les étapes sont passées avec succès !")
    
    print("\n📋 Prochaines étapes:")
    print("1. Modifiez le fichier .env avec vos paramètres")
    print("2. Testez l'installation: python test_installation.py")
    print("3. Lancez l'application: python start.py")
    print("\n📚 Documentation: README.md")

if __name__ == "__main__":
    main()
