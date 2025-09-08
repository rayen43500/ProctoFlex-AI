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

# Stockage en mémoire (simulation)
USERS: dict[str, dict] = {
    # Utilisateurs de démo
    "admin": {"username": "admin", "email": "admin@proctoflex.ai", "full_name": "Administrateur", "password": "admin123", "role": "admin"},
    "student": {"username": "student", "email": "student@test.com", "full_name": "Étudiant Démo", "password": "student123", "role": "student"},
}
EMAIL_INDEX: dict[str, str] = {"admin@proctoflex.ai": "admin", "student@test.com": "student"}
FACE_INDEX: dict[str, str] = {}

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
    username_or_email = credentials.get("username", "")
    password = credentials.get("password", "")

    # Chercher par username direct
    user = USERS.get(username_or_email)
    # Ou par email
    if not user:
        key = EMAIL_INDEX.get(username_or_email)
        if key:
            user = USERS.get(key)

    if user and user.get("password") == password:
        token = f"fake_token_{user['username']}_123"
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": 999 if user["username"] not in ("admin", "student") else (1 if user["username"]=="admin" else 2),
                "username": user["username"],
                "email": user["email"],
                "full_name": user.get("full_name", user["username"]),
                "role": user.get("role", "student"),
            }
        }

    raise HTTPException(status_code=401, detail="Identifiants invalides")

# Login avec visage (simulation)
@app.post("/api/v1/auth/login-with-face")
async def login_with_face(payload: dict):
    """
    Authentification par visage (simulée):
    - Si `face_image_base64` correspond à une empreinte déjà enregistrée, on connecte l'utilisateur.
    - Sinon, 401.
    """
    face_image_base64 = payload.get("face_image_base64")
    if not face_image_base64:
        raise HTTPException(status_code=400, detail="face_image_base64 requis")

    # Si identifiant fourni (email ou username), accepter si l'utilisateur existe (simulation tolérante)
    identifier = payload.get("username") or payload.get("email")
    user = None
    if identifier:
        user = USERS.get(identifier)
        if not user:
            key = EMAIL_INDEX.get(identifier)
            if key:
                user = USERS.get(key)

    # Sinon, tenter par empreinte exacte (simulation stricte)
    if not user:
        username = FACE_INDEX.get(face_image_base64)
        if username:
            user = USERS.get(username)

    if not user:
        raise HTTPException(status_code=401, detail="Visage non reconnu (simulation)")
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    token = f"fake_token_{user['username']}_123"
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": 999 if user["username"] not in ("admin", "student") else (1 if user["username"]=="admin" else 2),
            "username": user["username"],
            "email": user["email"],
            "full_name": user.get("full_name", user["username"]),
            "role": user.get("role", "student"),
        }
    }

# Inscription (simulée) avec vérification faciale optionnelle
@app.post("/api/v1/auth/register-with-face")
async def register_with_face(payload: dict):
    """
    Crée un compte utilisateur (simulation). Si `face_image_base64` est fourni,
    on simule la détection d'un visage et on accepte.
    """
    email = payload.get("email")
    username = payload.get("username")
    full_name = payload.get("full_name")
    password = payload.get("password")
    role = payload.get("role", "student")
    face_image_base64 = payload.get("face_image_base64")

    if not email or not username or not full_name or not password:
        raise HTTPException(status_code=400, detail="Champs requis manquants")

    # Simulation: si image présente, on considère qu'un visage est détecté
    if face_image_base64 is not None and len(str(face_image_base64)) < 10:
        raise HTTPException(status_code=400, detail="Aucun visage détecté (simulation)")

    # Sauvegarde en mémoire (simulation)
    USERS[username] = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password,
        "role": role,
    }
    EMAIL_INDEX[email] = username
    if face_image_base64:
        FACE_INDEX[face_image_base64] = username

    # Retour d'un token factice
    return {
        "access_token": "fake_token_registered_123",
        "token_type": "bearer",
        "user": {
            "id": 999,
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": role
        }
    }

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

# Alias simples pour l'app desktop (routes plus courtes)
@app.post("/api/v1/surveillance/start")
async def surveillance_start_simple():
    return {"success": True, "message": "Surveillance démarrée (simple)"}

@app.post("/api/v1/surveillance/stop")
async def surveillance_stop_simple():
    return {"success": True, "message": "Surveillance arrêtée (simple)"}

from datetime import datetime
from PIL import Image, ImageStat
import base64, io

@app.post("/api/v1/surveillance/analyze")
async def surveillance_analyze(payload: dict):
    """
    Analyse simplifiée et déterministe (pas d'aléatoire):
    - no_frame: si frame manquante
    - low_light: si luminosité moyenne très faible
    - blur_suspected: si variance faible (image très homogène)
    """
    timestamp = payload.get("timestamp") or datetime.utcnow().isoformat()
    video_frame = payload.get("video_frame")  # base64 data URL ou base64 pur

    alerts = []
    if not video_frame:
        alerts.append({"type": "no_frame", "severity": "high", "message": "Aucune image reçue"})
    else:
        try:
            data = video_frame.split(',')[1] if ',' in video_frame else video_frame
            img_bytes = base64.b64decode(data)
            img = Image.open(io.BytesIO(img_bytes)).convert('L')  # gris
            stat = ImageStat.Stat(img)
            mean_brightness = stat.mean[0]
            # variance approx via var[0]
            variance = stat.var[0] if hasattr(stat, 'var') else 0.0

            if mean_brightness < 25:
                alerts.append({"type": "low_light", "severity": "medium", "message": "Luminosité très faible"})
            if variance < 50:
                alerts.append({"type": "blur_suspected", "severity": "medium", "message": "Image trop uniforme (possible flou/occlusion)"})
        except Exception:
            alerts.append({"type": "decode_error", "severity": "low", "message": "Impossible d'analyser l'image"})

    overall_risk = "low"
    if any(a["severity"] == "high" for a in alerts):
        overall_risk = "high"
    elif any(a["severity"] == "medium" for a in alerts):
        overall_risk = "medium"

    return {"timestamp": timestamp, "alerts": alerts, "overall_risk": overall_risk}

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
