#!/usr/bin/env python3
"""
Script d'installation pour ProctoFlex AI Backend
Gère l'installation des dépendances et la configuration initiale
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} réussi")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} échoué")
        print(f"Erreur: {e.stderr}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ est requis")
        print(f"Version actuelle: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} détecté")
    return True

def install_dependencies():
    """Installe les dépendances Python"""
    print("\n📦 Installation des dépendances...")
    
    # Mettre à jour pip
    if not run_command("python -m pip install --upgrade pip", "Mise à jour de pip"):
        return False
    
    # Détecter le système d'exploitation
    import platform
    system = platform.system().lower()
    print(f"🖥️  Système détecté: {system}")
    
    # Choisir le bon fichier de dépendances
    if system == "windows":
        print("🪟 Windows détecté - Utilisation des dépendances compatibles")
        requirements_file = "requirements-windows.txt"
    else:
        print("🐧 Linux/Mac détecté - Utilisation des dépendances standard")
        requirements_file = "requirements.txt"
    
    # Installer les dépendances principales
    if not run_command(f"pip install -r {requirements_file}", f"Installation des dépendances principales ({requirements_file})"):
        return False
    
    # Installer les dépendances de développement (optionnel)
    dev_choice = input("\n🤔 Installer les dépendances de développement ? (y/n): ").lower()
    if dev_choice in ['y', 'yes', 'o', 'oui']:
        if not run_command("pip install -r requirements-dev.txt", "Installation des dépendances de développement"):
            print("⚠️  Installation des dépendances de développement échouée, mais l'installation principale est réussie")
    
    return True

def create_env_file():
    """Crée le fichier .env s'il n'existe pas"""
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
        print("⚠️  N'oubliez pas de modifier les valeurs par défaut !")
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
    print("🚀 Installation de ProctoFlex AI Backend")
    print("=" * 50)
    
    # Vérifier la version de Python
    if not check_python_version():
        sys.exit(1)
    
    # Installer les dépendances
    if not install_dependencies():
        print("\n❌ Installation échouée")
        sys.exit(1)
    
    # Créer le fichier .env
    if not create_env_file():
        print("\n⚠️  Erreur lors de la création du fichier .env")
    
    # Créer les répertoires
    if not create_directories():
        print("\n⚠️  Erreur lors de la création des répertoires")
    
    print("\n🎉 Installation terminée avec succès !")
    print("\n📋 Prochaines étapes:")
    print("1. Modifiez le fichier .env avec vos paramètres")
    print("2. Configurez votre base de données PostgreSQL")
    print("3. Lancez l'application: python main.py")
    print("\n📚 Documentation: README.md")

if __name__ == "__main__":
    main()
