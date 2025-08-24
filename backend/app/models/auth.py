"""
Modèles Pydantic pour l'authentification ProctoFlex AI
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """Modèle de token d'authentification"""
    access_token: str
    token_type: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None

class TokenData(BaseModel):
    """Données du token décodé"""
    username: Optional[str] = None

class UserBase(BaseModel):
    """Modèle de base pour les utilisateurs"""
    email: EmailStr
    username: str
    full_name: str
    role: str = "student"

class UserCreate(UserBase):
    """Modèle pour la création d'utilisateur"""
    password: str

class UserUpdate(BaseModel):
    """Modèle pour la mise à jour d'utilisateur"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    """Modèle complet d'utilisateur"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserInDB(User):
    """Modèle d'utilisateur avec mot de passe hashé (pour la base de données)"""
    hashed_password: str
