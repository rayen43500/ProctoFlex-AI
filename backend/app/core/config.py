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
    DATABASE_URL: str = "postgresql://user:password@localhost/proctoflex_db"
    
    # Sécurité
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend React
        "http://localhost:5173",  # Frontend Vite
        "http://localhost:8080",  # Client Electron
    ]
    
    # IA et Surveillance
    FACE_RECOGNITION_CONFIDENCE: float = 0.8
    GAZE_DETECTION_ENABLED: bool = True
    AUDIO_ANALYSIS_ENABLED: bool = True
    SCREEN_ANALYSIS_ENABLED: bool = True
    
    # Stockage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    RETENTION_DAYS: int = 90  # Conformité RGPD
    
    # WebSocket
    WEBSOCKET_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instance globale des paramètres
settings = Settings()

# Création du dossier d'upload s'il n'existe pas
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
