"""
Endpoints d'authentification ProctoFlex AI
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db, User
from app.core.security import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    get_password_hash,
    verify_password
)
from app.core.config import settings
from app.models.auth import Token, UserCreate, User
from pydantic import BaseModel
from typing import Optional
from app.ai.face_detection import face_detection_service
from app.crud.user import create_user, get_user_by_email

router = APIRouter()

class LoginRequest(BaseModel):
    """Modèle pour la requête de connexion"""
    username: str  # Peut être un email ou un nom d'utilisateur
    password: str

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authentification utilisateur et génération de token JWT
    Accepte l'email ou le nom d'utilisateur
    """
    # Essayer d'abord avec le nom d'utilisateur
    user = authenticate_user(db, login_data.username, login_data.password)
    
    # Si ça ne marche pas, essayer avec l'email
    if not user:
        # Vérifier si c'est un email
        if "@" in login_data.username:
            user = db.query(User).filter(User.email == login_data.username).first()
            if user and verify_password(login_data.password, user.hashed_password):
                pass  # Utilisateur trouvé avec l'email
            else:
                user = None
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compte utilisateur inactif"
        )
    
    # Création du token d'accès
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

class UserCreateWithFace(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    role: str = "student"
    face_image_base64: Optional[str] = None

@router.post("/register-with-face", response_model=Token)
async def register_with_face(
    user_data: UserCreateWithFace,
    db: Session = Depends(get_db)
):
    """
    Création d'un nouveau compte utilisateur avec vérification faciale optionnelle.
    - Si `face_image_base64` est fourni, on vérifie qu'un visage est détecté.
    """
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )

    # Vérification faciale (optionnelle)
    if user_data.face_image_base64:
        try:
            decoded = face_detection_service.decode_base64_image(user_data.face_image_base64)
            faces = face_detection_service.detect_faces(decoded)
            if not faces or len(faces) == 0:
                raise HTTPException(status_code=400, detail="Aucun visage détecté")
        except HTTPException:
            raise
        except Exception:
            # En cas d'indisponibilité des dépendances IA, accepter l'inscription mais notifier
            pass

    # Création utilisateur
    create_payload = UserCreate(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password=user_data.password,
        role=user_data.role,
    )
    user = create_user(db, create_payload)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Création d'un nouveau compte utilisateur
    """
    # Vérification que l'email n'existe pas déjà
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Création de l'utilisateur
    user = create_user(db, user_data)
    
    # Génération du token d'accès
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return current_user

@router.post("/logout")
async def logout():
    """
    Déconnexion de l'utilisateur
    Note: Avec JWT, la déconnexion se fait côté client en supprimant le token
    """
    return {"message": "Déconnexion réussie"}

@router.post("/refresh")
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Rafraîchit le token d'accès de l'utilisateur
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
