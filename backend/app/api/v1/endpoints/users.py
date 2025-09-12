"""
Endpoints pour la gestion des utilisateurs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db, User
from app.models.user import UserResponse, UserCreate, UserUpdate, UserStats

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupérer la liste des utilisateurs avec filtres optionnels"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/stats", response_model=UserStats)
async def get_user_stats(db: Session = Depends(get_db)):
    """Récupérer les statistiques des utilisateurs"""
    total_users = db.query(User).count()
    students = db.query(User).filter(User.role == "student").count()
    admins = db.query(User).filter(User.role == "admin").count()
    instructors = db.query(User).filter(User.role == "instructor").count()
    
    # Utilisateurs actifs aujourd'hui (créés ou mis à jour aujourd'hui)
    today = datetime.now().date()
    active_today = db.query(User).filter(
        User.created_at >= today,
        User.is_active == True
    ).count()
    
    return UserStats(
        total_users=total_users,
        students=students,
        admins=admins,
        instructors=instructors,
        active_today=active_today
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Récupérer un utilisateur par son ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouvel utilisateur"""
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Vérifier si le nom d'utilisateur existe déjà
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    
    # Créer l'utilisateur
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=user.password,  # En production, hasher le mot de passe
        role=user.role,
        is_active=user.is_active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un utilisateur"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Vérifier l'email unique si modifié
    if user.email and user.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Vérifier le nom d'utilisateur unique si modifié
    if user.username and user.username != db_user.username:
        existing_username = db.query(User).filter(User.username == user.username).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
    
    # Mettre à jour les champs
    update_data = user.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Supprimer un utilisateur (soft delete)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Soft delete - désactiver l'utilisateur
    db_user.is_active = False
    db_user.updated_at = datetime.now()
    db.commit()
    
    return {"message": "Utilisateur supprimé avec succès"}

@router.patch("/{user_id}/toggle-status")
async def toggle_user_status(user_id: int, db: Session = Depends(get_db)):
    """Activer/Désactiver un utilisateur"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db_user.is_active = not db_user.is_active
    db_user.updated_at = datetime.now()
    db.commit()
    
    return {
        "message": f"Utilisateur {'activé' if db_user.is_active else 'désactivé'} avec succès",
        "is_active": db_user.is_active
    }