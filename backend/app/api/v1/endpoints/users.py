"""
Endpoints API pour la gestion des utilisateurs
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from app.core.security import get_current_user
from app.models.user import User
from app.core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Modèles Pydantic
class UserCreate(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    role: str = "student"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère la liste des utilisateurs"""
    try:
        # Simulation pour l'instant
        users = [
            {
                "id": 1,
                "email": "admin@proctoflex.ai",
                "username": "admin",
                "full_name": "Administrateur ProctoFlex",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.now()
            },
            {
                "id": 2,
                "email": "student@test.com",
                "username": "student1",
                "full_name": "Étudiant Test",
                "role": "student",
                "is_active": True,
                "created_at": datetime.now()
            }
        ]
        return users
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des utilisateurs")

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouvel utilisateur"""
    try:
        # Simulation pour l'instant
        new_user = {
            "id": 1,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": True,
            "created_at": datetime.now()
        }
        return new_user
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'utilisateur")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère un utilisateur par son ID"""
    try:
        # Simulation pour l'instant
        user = {
            "id": user_id,
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Utilisateur Test",
            "role": "student",
            "is_active": True,
            "created_at": datetime.now()
        }
        return user
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'utilisateur")

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour un utilisateur"""
    try:
        # Simulation pour l'instant
        updated_user = {
            "id": user_id,
            "email": user_update.email or "test@example.com",
            "username": user_update.username or "testuser",
            "full_name": user_update.full_name or "Utilisateur Test",
            "role": user_update.role or "student",
            "is_active": user_update.is_active if user_update.is_active is not None else True,
            "created_at": datetime.now()
        }
        return updated_user
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'utilisateur {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour de l'utilisateur")

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime un utilisateur"""
    try:
        # Simulation pour l'instant
        return {"message": f"Utilisateur {user_id} supprimé avec succès"}
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'utilisateur {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression de l'utilisateur")
