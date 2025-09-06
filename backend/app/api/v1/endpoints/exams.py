"""
Endpoints API pour la gestion des examens
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
class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    allowed_apps: Optional[List[str]] = []
    allowed_domains: Optional[List[str]] = []

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    allowed_apps: Optional[List[str]] = None
    allowed_domains: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ExamResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration_minutes: int
    start_time: datetime
    end_time: datetime
    student_id: Optional[int]
    instructor_id: Optional[int]
    allowed_apps: Optional[List[str]]
    allowed_domains: Optional[List[str]]
    is_active: bool
    created_at: datetime

@router.get("/", response_model=List[ExamResponse])
async def get_exams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère la liste des examens"""
    try:
        # Simulation pour l'instant - remplacer par vraie requête DB
        exams = [
            {
                "id": 1,
                "title": "Examen de Programmation",
                "description": "Examen sur les concepts de programmation",
                "duration_minutes": 120,
                "start_time": datetime.now(),
                "end_time": datetime.now(),
                "student_id": 1,
                "instructor_id": 1,
                "allowed_apps": ["vscode", "browser"],
                "allowed_domains": ["github.com", "stackoverflow.com"],
                "is_active": True,
                "created_at": datetime.now()
            }
        ]
        return exams
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des examens: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des examens")

@router.post("/", response_model=ExamResponse)
async def create_exam(
    exam: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouvel examen"""
    try:
        # Simulation pour l'instant - remplacer par vraie création DB
        new_exam = {
            "id": 1,
            **exam.dict(),
            "student_id": current_user.id,
            "instructor_id": current_user.id,
            "is_active": True,
            "created_at": datetime.now()
        }
        return new_exam
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'examen: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'examen")

@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère un examen par son ID"""
    try:
        # Simulation pour l'instant
        exam = {
            "id": exam_id,
            "title": "Examen de Programmation",
            "description": "Examen sur les concepts de programmation",
            "duration_minutes": 120,
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "student_id": 1,
            "instructor_id": 1,
            "allowed_apps": ["vscode", "browser"],
            "allowed_domains": ["github.com", "stackoverflow.com"],
            "is_active": True,
            "created_at": datetime.now()
        }
        return exam
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'examen {exam_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'examen")

@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: int,
    exam_update: ExamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour un examen"""
    try:
        # Simulation pour l'instant
        updated_exam = {
            "id": exam_id,
            "title": exam_update.title or "Examen de Programmation",
            "description": exam_update.description or "Examen sur les concepts de programmation",
            "duration_minutes": exam_update.duration_minutes or 120,
            "start_time": exam_update.start_time or datetime.now(),
            "end_time": exam_update.end_time or datetime.now(),
            "student_id": 1,
            "instructor_id": 1,
            "allowed_apps": exam_update.allowed_apps or ["vscode", "browser"],
            "allowed_domains": exam_update.allowed_domains or ["github.com", "stackoverflow.com"],
            "is_active": exam_update.is_active if exam_update.is_active is not None else True,
            "created_at": datetime.now()
        }
        return updated_exam
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'examen {exam_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour de l'examen")

@router.delete("/{exam_id}")
async def delete_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime un examen"""
    try:
        # Simulation pour l'instant
        return {"message": f"Examen {exam_id} supprimé avec succès"}
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'examen {exam_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression de l'examen")
