"""
ProctoFlex AI - Backend API (Version Simplifiée)
Serveur FastAPI pour la surveillance d'examens en ligne
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import List
from sqlalchemy import func
from fastapi import Header
import logging
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la base de données
import os as _os, os
from pathlib import Path
DB_REQUIRED = _os.getenv("DB_REQUIRED", "true").lower() in ("1", "true", "yes")

def _default_db_url() -> str:
    # Si on est dans un conteneur Docker, utiliser le hostname du service postgres
    try:
        if Path("/.dockerenv").exists() or _os.getenv("DOCKER") == "true" or _os.getenv("INSIDE_DOCKER") == "1":
            return "postgresql://postgres:secure_password@postgres:5432/proctoflex"
    except Exception:
        pass
    # Sinon, fallback local
    return "postgresql://postgres:secure_password@localhost:5432/proctoflex"

DATABASE_URL = _os.getenv("DATABASE_URL", _default_db_url())

logger.info(f"Using DATABASE_URL: {DATABASE_URL}")
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    
    # Modèles de base de données
    class UserDB(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True, nullable=False)
        username = Column(String, unique=True, index=True, nullable=False)
        full_name = Column(String, nullable=False)
        hashed_password = Column(String, nullable=False)
        role = Column(String, default="student")
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    class ExamDB(Base):
        __tablename__ = "exams"
        id = Column(Integer, primary_key=True, index=True)
        title = Column(String, nullable=False)
        description = Column(Text)
        duration_minutes = Column(Integer, nullable=False)
        instructions = Column(Text)
        status = Column(String, default="draft")
        start_time = Column(DateTime(timezone=True))
        end_time = Column(DateTime(timezone=True))
        instructor_id = Column(Integer, ForeignKey("users.id"))
        allowed_apps = Column(Text)
        allowed_domains = Column(Text)
        pdf_path = Column(String)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    class ExamStudentDB(Base):
        __tablename__ = "exam_students"
        id = Column(Integer, primary_key=True, index=True)
        exam_id = Column(Integer, ForeignKey("exams.id"))
        student_id = Column(Integer, ForeignKey("users.id"))
        assigned_at = Column(DateTime(timezone=True), server_default=func.now())
        status = Column(String, default="assigned")  # assigned, started, completed, failed
    
    # Test de connexion
    with engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text("SELECT 1"))
    DB_OK = True
    logger.info("✅ Connexion à la base de données réussie")
except Exception as e:
    logger.warning(f"⚠️ Base de données non disponible: {e}")
    DB_OK = False
    UserDB = None
    ExamDB = None
    SessionLocal = None

# En mode strict (par défaut), ne pas démarrer si la DB n'est pas disponible
if DB_REQUIRED and not DB_OK:
    logger.error("❌ PostgreSQL est requis (DB_REQUIRED=true) mais indisponible. Arrêt du serveur.")
    raise SystemExit(1)

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
USERS: dict[str, dict] = {}
EMAIL_INDEX: dict[str, str] = {}
FACE_INDEX: dict[str, str] = {}

# Sécurité: hachage mot de passe (bcrypt si dispo)
try:
    import bcrypt  # type: ignore
    def hash_password(pw: str) -> str:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    def verify_password(pw: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(pw.encode(), hashed.encode())
        except Exception:
            return pw == hashed
except Exception:
    def hash_password(pw: str) -> str:
        return pw  # fallback non sécurisé (dev-only)
    def verify_password(pw: str, hashed: str) -> bool:
        return pw == hashed

# Utilisateurs de démo (admin/student)
def _bootstrap_users():
    admin_h = hash_password("admin123")
    student_h = hash_password("student123")
    USERS["admin"] = {"username": "admin", "email": "admin@proctoflex.ai", "full_name": "Administrateur", "password": admin_h, "role": "admin"}
    USERS["student"] = {"username": "student", "email": "student@test.com", "full_name": "Étudiant Démo", "password": student_h, "role": "student"}
    EMAIL_INDEX["admin@proctoflex.ai"] = "admin"
    EMAIL_INDEX["student@test.com"] = "student"
    # Réplication optionnelle en base si disponible
    if DB_OK and SessionLocal is not None and UserDB is not None:
        try:
            with SessionLocal() as db:
                # Admin
                existing_admin = db.query(UserDB).filter((UserDB.username == "admin") | (UserDB.email == "admin@proctoflex.ai")).first()
                if not existing_admin:
                    db.add(UserDB(
                        email="admin@proctoflex.ai",
                        username="admin",
                        full_name="Administrateur",
                        hashed_password=admin_h,
                        role="admin",
                        is_active=True
                    ))
                # Student demo
                existing_student = db.query(UserDB).filter((UserDB.username == "student") | (UserDB.email == "student@test.com")).first()
                if not existing_student:
                    db.add(UserDB(
                        email="student@test.com",
                        username="student",
                        full_name="Étudiant Démo",
                        hashed_password=student_h,
                        role="student",
                        is_active=True
                    ))
                db.commit()
        except Exception as _e:
            logger.warning(f"Bootstrap DB users skipped: {_e}")

_bootstrap_users()

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

# Routes API de base - Supprimées car remplacées par les endpoints complets plus bas


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
    """Authentification avec base de données PostgreSQL"""
    # Accepter 'username' ou 'email' comme identifiant
    username_or_email = str(
        credentials.get("username")
        or credentials.get("email")
        or ""
    ).strip()
    password = str(credentials.get("password", ""))
    ident_lower = username_or_email.lower()

    # 1) Si la DB est disponible, tenter l'authentification en base
    if DB_OK:
        with SessionLocal() as db:
            # Chercher par email ou username (base de données)
            user_db = db.query(UserDB).filter(
                (func.lower(UserDB.email) == ident_lower) | (func.lower(UserDB.username) == ident_lower)
            ).first()
            if user_db and verify_password(password, user_db.hashed_password):
                token = f"fake_token_{user_db.username}_123"
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user_db.id,
                        "username": user_db.username,
                        "email": user_db.email,
                        "full_name": user_db.full_name,
                        "role": user_db.role,
                    }
                }

    # 2) Fallback mémoire (utile en dev lorsque la DB est partiellement remplie
    #    ou pour les comptes bootstrapés). On n'utilise ce fallback que si
    #    l'authentification en base a échoué.
    try:
        # Trouver par username exact (clé) ou par email index
        key = None
        if username_or_email in USERS:
            key = username_or_email
        else:
            # Chercher email insensitive
            for em, uname in EMAIL_INDEX.items():
                if em.lower() == ident_lower:
                    key = uname
                    break

        if key:
            mem_user = USERS.get(key)
            if mem_user and verify_password(password, mem_user.get("password") or ""):
                token = f"fake_token_{mem_user['username']}_123"
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": 999,  # mémoire: id fictif
                        "username": mem_user["username"],
                        "email": mem_user.get("email"),
                        "full_name": mem_user.get("full_name", mem_user["username"]),
                        "role": mem_user.get("role", "student"),
                    }
                }
    except Exception:
        # Ne jamais exposer d'erreurs internes d'authentification
        pass

    # 3) Si la DB est active, renvoyer 401 (identifiants invalides). Si la DB
    #    est indisponible, renvoyer 503.
    if DB_OK:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    raise HTTPException(status_code=503, detail="Base de données indisponible")

# Profil utilisateur courant
@app.get("/api/v1/auth/me")
async def auth_me(authorization: str | None = Header(default=None)):
    """Retourne l'utilisateur courant sur base du token (format simulé)."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    token = authorization.split(" ", 1)[1]
    username = None
    # Token simulé: fake_token_<username>_123
    if token.startswith("fake_token_") and token.endswith("_123"):
        try:
            username = token[len("fake_token_"):-len("_123")]
        except Exception:
            username = None

    if not username:
        raise HTTPException(status_code=401, detail="Token invalide")

    if DB_OK:
        with SessionLocal() as db:
            user_db = db.query(UserDB).filter(UserDB.username == username).first()
            if user_db:
                return {
                    "id": user_db.id,
                    "email": user_db.email,
                    "username": user_db.username,
                    "full_name": user_db.full_name,
                    "role": user_db.role,
                    "is_active": user_db.is_active,
                }

    # Pas de fallback mémoire
    raise HTTPException(status_code=503, detail="Base de données indisponible")

# Login avec visage (simulation)
@app.post("/api/v1/auth/login-with-face")
async def login_with_face(payload: dict):
    """
    Authentification par visage avec base de données PostgreSQL.
    """
    face_image_base64 = payload.get("face_image_base64")
    if not face_image_base64:
        raise HTTPException(status_code=400, detail="face_image_base64 requis")

    # Si identifiant fourni (email ou username), accepter si l'utilisateur existe
    identifier = payload.get("username") or payload.get("email")
    user = None
    
    if DB_OK:
        with SessionLocal() as db:
            if identifier:
                user = db.query(UserDB).filter(
                    (UserDB.email == identifier) | (UserDB.username == identifier)
                ).first()
            
            # Sinon, tenter par empreinte exacte (simulation stricte)
            if not user:
                username = FACE_INDEX.get(face_image_base64)
                if username:
                    user = db.query(UserDB).filter(UserDB.username == username).first()
    else:
        # Fallback sur les données en mémoire
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
        raise HTTPException(status_code=401, detail="Visage non reconnu")

    if DB_OK:
        token = f"fake_token_{user.username}_123"
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
            }
        }
    else:
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
    Crée un compte utilisateur avec base de données PostgreSQL.
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

    if DB_OK:
        with SessionLocal() as db:
            # Vérifier si l'utilisateur existe déjà
            existing_user = db.query(UserDB).filter(
                (UserDB.email == email) | (UserDB.username == username)
            ).first()
            
            if existing_user:
                raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
            
            # Créer le nouvel utilisateur
            new_user = UserDB(
                email=email,
                username=username,
                full_name=full_name,
                hashed_password=hash_password(password),
                role=role,
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Sauvegarder l'empreinte faciale en mémoire (simulation)
            if face_image_base64:
                FACE_INDEX[face_image_base64] = username
            
            return {
                "access_token": f"fake_token_{username}_123",
                "token_type": "bearer",
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "full_name": new_user.full_name,
                    "role": new_user.role
                }
            }
    # Pas de fallback mémoire
    raise HTTPException(status_code=503, detail="Base de données indisponible")

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

# --- Consentement RGPD ---
CONSENTS: list[dict] = []

@app.post("/api/v1/auth/consent")
async def record_consent(payload: dict):
    CONSENTS.append({
        "user": payload.get("user"),
        "consent": bool(payload.get("consent", False)),
        "timestamp": payload.get("timestamp"),
        "version": payload.get("version", "1.0")
    })
    return {"success": True}

# --- Timeline d'alertes ---
ALERTS: list[dict] = []

@app.get("/api/v1/alerts")
async def list_alerts(student: str | None = None):
    if student:
        return [a for a in ALERTS if str(a.get("student", "")).lower() == student.lower()][-500:]
    return ALERTS[-500:]

@app.post("/api/v1/alerts")
async def push_alert(alert: dict):
    # Normaliser le champ étudiant
    student = alert.get("student")
    if isinstance(student, dict):
        # Garder info minimale
        alert["student"] = student.get("email") or student.get("username") or student.get("id")
    ALERTS.append(alert)
    return {"success": True}

# --- Examens CRUD (simulé) ---
from uuid import uuid4
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
import os

# --- Persistence PostgreSQL pour Examens (SQLAlchemy) ---
# Configuration de base de données déplacée en haut du fichier

if DB_OK:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as _e:
        print(f"[main_simple] Warning: create_all failed: {_e}")
        DB_OK = False
EXAMS: dict[str, dict] = {}

@app.get("/api/v1/exams")
async def exams_list():
    if DB_OK:
        with SessionLocal() as db:
            rows = db.query(ExamDB).all()
            return [
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "duration_minutes": r.duration_minutes,
                    "status": r.status,
                    "instructions": r.instructions,
                    "created_at": r.created_at,
                    "pdf_path": r.pdf_path,
                } for r in rows
            ]
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.post("/api/v1/exams")
async def exams_create(payload: dict):
    if DB_OK:
        with SessionLocal() as db:
            # Créer l'examen
            row = ExamDB(
                title=payload.get("title", "Examen"),
                description=payload.get("description", ""),
                duration_minutes=int(payload.get("duration_minutes", 60)),
                status=payload.get("status", "draft"),
                instructions=payload.get("instructions", ""),
                instructor_id=payload.get("instructor_id", 1),  # ID de l'instructeur
                created_at=payload.get("created_at", "2025-01-15T10:00:00Z"),
                pdf_path=None,
            )
            db.add(row)
            db.commit()
            
            # Assigner les étudiants sélectionnés
            selected_students = payload.get("selected_students", [])
            for student_id in selected_students:
                exam_student = ExamStudentDB(
                    exam_id=row.id,
                    student_id=student_id,
                    status="assigned"
                )
                db.add(exam_student)
            
            db.commit()
            
            return {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "duration_minutes": row.duration_minutes,
                "status": row.status,
                "instructions": row.instructions,
                "instructor_id": row.instructor_id,
                "selected_students": selected_students,
                "created_at": row.created_at,
                "pdf_path": row.pdf_path,
            }
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.put("/api/v1/exams/{exam_id}")
async def exams_update(exam_id: str, payload: dict):
    if DB_OK:
        with SessionLocal() as db:
            row = db.query(ExamDB).get(exam_id)
            if not row:
                raise HTTPException(status_code=404, detail="Examen introuvable")
            for k, v in payload.items():
                if hasattr(row, k):
                    setattr(row, k, v)
            db.commit()
            db.refresh(row)
            return {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "duration_minutes": row.duration_minutes,
                "status": row.status,
                "instructions": row.instructions,
                "created_at": row.created_at,
                "pdf_path": row.pdf_path,
            }
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.delete("/api/v1/exams/{exam_id}")
async def exams_delete(exam_id: str):
    if DB_OK:
        try:
            # Normalize exam_id to integer if possible
            try:
                exam_pk = int(exam_id)
            except Exception:
                # If not numeric, return 400
                raise HTTPException(status_code=400, detail="Identifiant d'examen invalide")

            with SessionLocal() as db:
                # First remove any exam_students entries to avoid FK constraint errors
                try:
                    db.query(ExamStudentDB).filter(ExamStudentDB.exam_id == exam_pk).delete()
                except Exception:
                    # Log but continue to attempt exam deletion
                    logger.exception("Erreur lors de la suppression des liaisons exam_students")

                row = db.query(ExamDB).filter(ExamDB.id == exam_pk).first()
                if row:
                    # If there's an associated pdf file, attempt to remove it from disk
                    try:
                        if row.pdf_path:
                            pdf_path = os.path.join(os.getcwd(), 'uploads', 'exams', row.pdf_path)
                            if os.path.exists(pdf_path):
                                os.remove(pdf_path)
                    except Exception:
                        logger.exception("Impossible de supprimer le fichier PDF lié à l'examen")

                    db.delete(row)
                    db.commit()
                    return {"success": True}

                # If row not found, return 404
                raise HTTPException(status_code=404, detail="Examen introuvable")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Erreur interne lors de la suppression de l'examen {exam_id}: {e}")
            raise HTTPException(status_code=500, detail="Erreur interne lors de la suppression de l'examen")
    # DB not available
    raise HTTPException(status_code=503, detail="Base de données indisponible")

# --- Ressources d'examen (PDF) ---
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "exams")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/exams/{exam_id}/material")
async def upload_exam_material(exam_id: str, file: UploadFile = File(...)):
    if DB_OK:
        with SessionLocal() as db:
            row = db.query(ExamDB).get(exam_id)
            if not row:
                raise HTTPException(status_code=404, detail="Examen introuvable")
    # Sauvegarde du PDF
    filename = f"{exam_id}.pdf"
    dest = os.path.join(UPLOAD_DIR, filename)
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)
    if DB_OK:
        row.pdf_path = filename
        db.commit()
    return {"success": True, "filename": filename}

@app.get("/api/v1/exams/{exam_id}/material")
async def get_exam_material(exam_id: str):
    filename = None
    if DB_OK:
        with SessionLocal() as db:
            row = db.query(ExamDB).get(exam_id)
            if not row or not row.pdf_path:
                raise HTTPException(status_code=404, detail="Aucun document")
            filename = row.pdf_path
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    return FileResponse(path, media_type="application/pdf", filename=filename)

# --- Démarrer / Soumettre un examen (compatibilité App Desktop) ---
@app.post("/api/v1/exams/{exam_id}/start")
async def start_exam_simple(exam_id: int, student_id: int):
    """Démarre un examen pour un étudiant: met exam_students.status à 'started'"""
    if not DB_OK:
        raise HTTPException(status_code=503, detail="Base de données indisponible")
    with SessionLocal() as db:
        exam_student = db.query(ExamStudentDB).filter(
            ExamStudentDB.exam_id == exam_id,
            ExamStudentDB.student_id == student_id
        ).first()
        if not exam_student:
            raise HTTPException(status_code=404, detail="Examen non assigné à cet étudiant")
        if exam_student.status == "completed":
            return {"message": "Examen déjà soumis", "exam_id": exam_id, "status": exam_student.status}
        exam_student.status = "started"
        db.commit()
        return {"message": "Examen démarré", "exam_id": exam_id, "status": exam_student.status}

@app.post("/api/v1/exams/{exam_id}/submit")
async def submit_exam_simple(exam_id: int, student_id: int, answers: dict | None = None):
    """Soumet un examen pour un étudiant: met exam_students.status à 'completed'"""
    if not DB_OK:
        raise HTTPException(status_code=503, detail="Base de données indisponible")
    with SessionLocal() as db:
        exam_student = db.query(ExamStudentDB).filter(
            ExamStudentDB.exam_id == exam_id,
            ExamStudentDB.student_id == student_id
        ).first()
        if not exam_student:
            raise HTTPException(status_code=404, detail="Examen non assigné à cet étudiant")
        exam_student.status = "completed"
        db.commit()
        return {"message": "Examen soumis", "exam_id": exam_id, "status": exam_student.status}

# --- Endpoints pour les étudiants ---
@app.get("/api/v1/students/{student_id}/exams")
async def get_student_exams(student_id: int):
    """Récupérer les examens assignés à un étudiant"""
    if DB_OK:
        with SessionLocal() as db:
            # Récupérer les examens assignés à l'étudiant
            exam_students = db.query(ExamStudentDB).filter(
                ExamStudentDB.student_id == student_id
            ).all()
            
            exams = []
            for exam_student in exam_students:
                exam = db.query(ExamDB).filter(ExamDB.id == exam_student.exam_id).first()
                if exam:
                    exams.append({
                        "id": exam.id,
                        "title": exam.title,
                        "description": exam.description,
                        "duration_minutes": exam.duration_minutes,
                        "instructions": exam.instructions,
                        "status": exam.status,
                        "pdf_path": exam.pdf_path,
                        "assigned_at": exam_student.assigned_at,
                        "exam_status": exam_student.status,
                        "created_at": exam.created_at
                    })
            
            return exams
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

# Alias de compatibilité pour l'app desktop
@app.get("/api/v1/exams/student/{student_id}")
async def get_student_exams_alias(student_id: int):
    return await get_student_exams(student_id)

@app.get("/api/v1/students/{student_id}/exams/{exam_id}")
async def get_student_exam_details(student_id: int, exam_id: str):
    """Récupérer les détails d'un examen spécifique pour un étudiant"""
    if DB_OK:
        with SessionLocal() as db:
            # Vérifier que l'examen est assigné à l'étudiant
            exam_student = db.query(ExamStudentDB).filter(
                ExamStudentDB.student_id == student_id,
                ExamStudentDB.exam_id == exam_id
            ).first()
            
            if not exam_student:
                raise HTTPException(status_code=404, detail="Examen non assigné à cet étudiant")
            
            exam = db.query(ExamDB).filter(ExamDB.id == exam_id).first()
            if not exam:
                raise HTTPException(status_code=404, detail="Examen non trouvé")
            
            return {
                "id": exam.id,
                "title": exam.title,
                "description": exam.description,
                "duration_minutes": exam.duration_minutes,
                "instructions": exam.instructions,
                "status": exam.status,
                "pdf_path": exam.pdf_path,
                "assigned_at": exam_student.assigned_at,
                "exam_status": exam_student.status,
                "created_at": exam.created_at
            }
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

# --- Endpoints Utilisateurs ---
@app.get("/api/v1/users")
async def get_users():
    """Récupérer la liste des utilisateurs"""
    if DB_OK:
        with SessionLocal() as db:
            users_db = db.query(UserDB).all()
            result = [
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                for user in users_db
            ]
            return result
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.get("/api/v1/users/stats")
async def get_user_stats():
    """Récupérer les statistiques des utilisateurs"""
    if DB_OK:
        with SessionLocal() as db:
            total_users = db.query(UserDB).count()
            students = db.query(UserDB).filter(UserDB.role == "student").count()
            admins = db.query(UserDB).filter(UserDB.role == "admin").count()
            instructors = db.query(UserDB).filter(UserDB.role == "instructor").count()
            
            # Utilisateurs actifs aujourd'hui
            from datetime import datetime, date
            today = date.today()
            active_today = db.query(UserDB).filter(
                UserDB.created_at >= today,
                UserDB.is_active == True
            ).count()
            
            return {
                "total_users": total_users,
                "students": students,
                "admins": admins,
                "instructors": instructors,
                "active_today": active_today
            }
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    """Récupérer un utilisateur par son ID"""
    if DB_OK:
        with SessionLocal() as db:
            user = db.query(UserDB).filter(UserDB.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.post("/api/v1/users")
async def create_user(user_data: dict):
    """Créer un nouvel utilisateur"""
    if DB_OK:
        with SessionLocal() as db:
            # Vérifier si l'email existe déjà
            existing_user = db.query(UserDB).filter(UserDB.email == user_data["email"]).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email déjà utilisé")
            
            # Vérifier si le nom d'utilisateur existe déjà
            existing_username = db.query(UserDB).filter(UserDB.username == user_data["username"]).first()
            if existing_username:
                raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
            
            # Créer l'utilisateur
            db_user = UserDB(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data.get("role", "student"),
                is_active=user_data.get("is_active", True)
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            return {
                "id": db_user.id,
                "email": db_user.email,
                "username": db_user.username,
                "full_name": db_user.full_name,
                "role": db_user.role,
                "is_active": db_user.is_active,
                "created_at": db_user.created_at,
                "updated_at": db_user.updated_at
            }
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.put("/api/v1/users/{user_id}")
async def update_user(user_id: int, user_data: dict):
    """Mettre à jour un utilisateur"""
    if DB_OK:
        with SessionLocal() as db:
            db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
            # Vérifier l'email unique si modifié
            if "email" in user_data and user_data["email"] != db_user.email:
                existing_user = db.query(UserDB).filter(UserDB.email == user_data["email"]).first()
                if existing_user:
                    raise HTTPException(status_code=400, detail="Email déjà utilisé")
            
            # Vérifier le nom d'utilisateur unique si modifié
            if "username" in user_data and user_data["username"] != db_user.username:
                existing_username = db.query(UserDB).filter(UserDB.username == user_data["username"]).first()
                if existing_username:
                    raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
            
            # Mettre à jour les champs
            for field, value in user_data.items():
                if field == "password":
                    setattr(db_user, "hashed_password", hash_password(value))
                elif hasattr(db_user, field):
                    setattr(db_user, field, value)
            
            db_user.updated_at = datetime.now()
            db.commit()
            db.refresh(db_user)
            
            return {
                "id": db_user.id,
                "email": db_user.email,
                "username": db_user.username,
                "full_name": db_user.full_name,
                "role": db_user.role,
                "is_active": db_user.is_active,
                "created_at": db_user.created_at,
                "updated_at": db_user.updated_at
            }
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: int):
    """Supprimer un utilisateur (soft delete)"""
    if DB_OK:
        with SessionLocal() as db:
            db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
            # Soft delete - désactiver l'utilisateur
            db_user.is_active = False
            db_user.updated_at = datetime.now()
            db.commit()
            
            return {"message": "Utilisateur supprimé avec succès"}
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

@app.patch("/api/v1/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: int):
    """Activer/Désactiver un utilisateur"""
    if DB_OK:
        with SessionLocal() as db:
            db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
            db_user.is_active = not db_user.is_active
            db_user.updated_at = datetime.now()
            db.commit()
            
            return {
                "message": f"Utilisateur {'activé' if db_user.is_active else 'désactivé'} avec succès",
                "is_active": db_user.is_active
            }
    
    raise HTTPException(status_code=503, detail="Base de données indisponible")

# --- Configuration de verrouillage (apps autorisées/interdites, domaines, politique) ---
LOCK_CONFIG = {
    "allowed_apps": ["code.exe", "excel.exe", "python.exe"],
    "forbidden_apps": ["discord.exe", "whatsapp.exe", "teams.exe", "chrome.exe", "msedge.exe", "firefox.exe"],
    "allowed_domains": ["proctoflex.ai", "docs.python.org"],
    "policy": {
        "auto_kill": False,
        "repeat_threshold": 2
    }
}

@app.get("/api/v1/config/lock")
async def get_lock_config():
    return LOCK_CONFIG

@app.put("/api/v1/config/lock")
async def update_lock_config(cfg: dict):
    LOCK_CONFIG["allowed_apps"] = list(cfg.get("allowed_apps", LOCK_CONFIG["allowed_apps"]))
    LOCK_CONFIG["forbidden_apps"] = list(cfg.get("forbidden_apps", LOCK_CONFIG.get("forbidden_apps", [])))
    LOCK_CONFIG["allowed_domains"] = list(cfg.get("allowed_domains", LOCK_CONFIG["allowed_domains"]))
    if "policy" in cfg and isinstance(cfg["policy"], dict):
        policy = LOCK_CONFIG.get("policy", {})
        policy["auto_kill"] = bool(cfg["policy"].get("auto_kill", policy.get("auto_kill", False)))
        policy["repeat_threshold"] = int(cfg["policy"].get("repeat_threshold", policy.get("repeat_threshold", 2)))
        LOCK_CONFIG["policy"] = policy
    return LOCK_CONFIG

# --- Upload d'enregistrements (webcam/micro/écran) ---
RECORDS: list[dict] = []

@app.post("/api/v1/records/upload")
async def upload_record(payload: dict):
    RECORDS.append({
        "type": payload.get("type"),  # video/audio/screen
        "session_id": payload.get("session_id"),
        "timestamp": payload.get("timestamp"),
        "size": len(payload.get("data", "")),
    })
    return {"success": True}

# --- IA: audio et écran (simulé) ---
@app.post("/api/v1/ai/analyze-audio")
async def analyze_audio(payload: dict):
    # Détection simple simulée
    duration = float(payload.get("duration", 0))
    has_voices = bool(payload.get("voices", False))
    alerts = []
    if has_voices and duration > 0:
        alerts.append({"type": "third_party_voice", "severity": "medium", "message": "Voix tierce détectée"})
    return {"alerts": alerts, "confidence": 0.7}

@app.post("/api/v1/ai/analyze-screen")
async def analyze_screen(payload: dict):
    active_app = payload.get("active_app")
    forbidden_list = [a.lower() for a in LOCK_CONFIG.get("forbidden_apps", [])]
    if active_app and active_app.lower() in forbidden_list:
        return {"alerts": [{"type": "forbidden_app", "severity": "high", "message": f"Application interdite: {active_app}"}]}
    if active_app and active_app.lower() not in [a.lower() for a in LOCK_CONFIG["allowed_apps"]]:
        return {"alerts": [{"type": "unlisted_app", "severity": "medium", "message": f"Application non listée: {active_app}"}]}
    return {"alerts": []}

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
