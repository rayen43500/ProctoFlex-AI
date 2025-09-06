"""
ProctoFlex AI - Backend API (Version Simplifiée)
Serveur FastAPI pour la surveillance d'examens en ligne
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from typing import List
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de base
app = FastAPI(
    title="ProctoFlex AI API",
    description="API de surveillance intelligente pour examens en ligne",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de santé
@app.get("/health")
async def health_check():
    """Vérification de l'état du serveur"""
    return {
        "status": "healthy",
        "service": "ProctoFlex AI Backend",
        "version": "1.0.0",
        "message": "Serveur opérationnel"
    }

# Route racine
@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue sur ProctoFlex AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Routes API de base
@app.get("/api/v1/users")
async def get_users():
    """Liste des utilisateurs (simulée)"""
    return [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@proctoflex.ai",
            "role": "admin",
            "is_active": True
        },
        {
            "id": 2,
            "username": "student1",
            "email": "student@test.com",
            "role": "student",
            "is_active": True
        }
    ]

@app.get("/api/v1/exams")
async def get_exams():
    """Liste des examens (simulée)"""
    return [
        {
            "id": 1,
            "title": "Examen de Programmation",
            "description": "Examen sur les concepts de programmation",
            "duration_minutes": 120,
            "status": "active",
            "created_at": "2025-01-15T10:00:00Z"
        },
        {
            "id": 2,
            "title": "Examen de Mathématiques",
            "description": "Examen de mathématiques avancées",
            "duration_minutes": 90,
            "status": "scheduled",
            "created_at": "2025-01-15T10:00:00Z"
        }
    ]

@app.get("/api/v1/sessions")
async def get_sessions():
    """Liste des sessions d'examen (simulée)"""
    return [
        {
            "id": 1,
            "exam_id": 1,
            "student_id": 2,
            "status": "active",
            "start_time": "2025-01-15T10:00:00Z",
            "risk_level": "low"
        }
    ]

@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    """Authentification (simulée)"""
    username = credentials.get("username", "")
    password = credentials.get("password", "")
    
    # Simulation d'authentification
    if username == "admin" and password == "admin123":
        return {
            "access_token": "fake_token_admin_123",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@proctoflex.ai",
                "role": "admin"
            }
        }
    elif username == "student" and password == "student123":
        return {
            "access_token": "fake_token_student_123",
            "token_type": "bearer",
            "user": {
                "id": 2,
                "username": "student",
                "email": "student@test.com",
                "role": "student"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Identifiants invalides")

# Routes de surveillance (simulées)
@app.post("/api/v1/surveillance/sessions/{session_id}/start")
async def start_surveillance_session(session_id: str):
    """Démarre une session de surveillance"""
    return {
        "success": True,
        "session_id": session_id,
        "message": "Session de surveillance démarrée",
        "timestamp": "2025-01-15T10:00:00Z"
    }

@app.post("/api/v1/surveillance/sessions/{session_id}/analyze")
async def analyze_surveillance_frame(session_id: str, data: dict):
    """Analyse un frame de surveillance (simulé)"""
    return {
        "success": True,
        "session_id": session_id,
        "risk_level": "low",
        "alerts_count": 0,
        "timestamp": "2025-01-15T10:00:00Z"
    }

@app.get("/api/v1/surveillance/health")
async def surveillance_health():
    """Vérifie l'état des services de surveillance"""
    return {
        "status": "healthy",
        "services": {
            "face_recognition": "simulated",
            "object_detection": "simulated",
            "audio_analysis": "simulated"
        },
        "message": "Services de surveillance simulés"
    }

# Routes IA (simulées)
@app.post("/api/v1/ai/verify-identity")
async def verify_identity(data: dict):
    """Vérification d'identité (simulée)"""
    return {
        "verified": True,
        "confidence": 0.95,
        "distance": 0.3,
        "threshold": 0.6,
        "reason": "Identité vérifiée avec succès (simulation)"
    }

@app.post("/api/v1/ai/analyze-face")
async def analyze_face(data: dict):
    """Analyse faciale (simulée)"""
    return {
        "faces_detected": 1,
        "face_quality": {
            "brightness": 0.8,
            "contrast": 0.7,
            "sharpness": 0.9
        },
        "multiple_faces": False,
        "gaze_analysis": {
            "looking_at_screen": True,
            "confidence": 0.85
        }
    }

@app.get("/api/v1/ai/health")
async def ai_health():
    """Vérifie l'état des services IA"""
    return {
        "status": "healthy",
        "services": {
            "face_detection": "simulated",
            "object_detection": "simulated",
            "audio_analysis": "simulated"
        },
        "message": "Services IA simulés"
    }

if __name__ == "__main__":
    print("🚀 Démarrage de ProctoFlex AI Backend (Version Simplifiée)")
    print("📍 API disponible sur: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
