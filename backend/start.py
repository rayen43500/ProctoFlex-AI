#!/usr/bin/env python3
"""
Script de démarrage optimisé pour ProctoFlex AI Backend
"""

import os
import sys
import uvicorn
from pathlib import Path
import logging
from app.core.config import settings

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Vérifie la configuration de l'environnement"""
    logger.info("🔍 Vérification de l'environnement...")
    
    # Vérifier les répertoires
    required_dirs = ["logs", "uploads"]
    for directory in required_dirs:
        if not Path(directory).exists():
            logger.warning(f"⚠️  Répertoire {directory} manquant")
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"✅ Répertoire {directory} créé")
    
    # Vérifier la configuration
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
        logger.warning("⚠️  SECRET_KEY par défaut détecté - changez-le en production!")
    
    logger.info("✅ Environnement configuré")
    return True

def start_server():
    """Démarre le serveur FastAPI"""
    logger.info("🚀 Démarrage du serveur ProctoFlex AI...")
    
    logger.info(f"📍 Serveur: http://{settings.HOST}:{settings.PORT}")
    logger.info(f"🔧 Mode debug: {settings.DEBUG}")
    logger.info(f"📁 Répertoire de travail: {os.getcwd()}")
    logger.info(f"🗄️  Base de données: {settings.DATABASE_URL}")
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🎯 ProctoFlex AI - Script de Démarrage Optimisé")
    print("=" * 50)
    
    # Vérifier l'environnement
    if not check_environment():
        logger.error("❌ Configuration manquante")
        sys.exit(1)
    
    # Démarrer le serveur
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()