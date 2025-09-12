"""
Configuration de l'application ProctoFlex AI
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Informations de base
    PROJECT_NAME: str = "ProctoFlex AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base de données
    # Format accepté: postgresql://user:pass@host:port/db  ou  mysql+pymysql://user:pass@host:3306/db  ou  sqlite:///./local.db
    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/proctoflex"
    DATABASE_TEST_URL: str = "sqlite:///./test.db"  # Utilisé dans les tests automatisés
    DB_ECHO: bool = False  # Activer SQLAlchemy echo pour debug

    # Support multi SGBD : si vous souhaitez utiliser MySQL, définissez DATABASE_URL avec le driver mysql+pymysql
    # Exemple: mysql+pymysql://user:pass@localhost:3306/proctoflex
    
    # Sécurité
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Serveur
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend React
        "http://localhost:5173",  # Frontend Vite
        "http://localhost:8080",  # Client Electron
    ]
    
    # IA et Surveillance
    FACE_RECOGNITION_CONFIDENCE: float = 0.8
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    MIN_FACE_CONFIDENCE: float = 0.8
    GAZE_DETECTION_ENABLED: bool = True
    AUDIO_ANALYSIS_ENABLED: bool = True
    SCREEN_ANALYSIS_ENABLED: bool = True
    AI_ENABLE_YOLO: bool = True  # Désactiver pour éviter le chargement du modèle en environnement contraint
    YOLO_MODEL_PATH: str = "models/yolov5s.pt"
    YOLO_AUTO_DOWNLOAD: bool = True  # Téléchargement automatique si le fichier manque
    
    # Stockage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    RETENTION_DAYS: int = 90  # Conformité RGPD
    
    # WebSocket
    WEBSOCKET_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Redis (optionnel)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instance globale des paramètres
settings = Settings()

# Création du dossier d'upload s'il n'existe pas
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
