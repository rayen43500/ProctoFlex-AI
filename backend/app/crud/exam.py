"""
Opérations CRUD pour les examens
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import json
from datetime import datetime

from app.core.database import Exam
from app.models.exam import ExamCreate, ExamUpdate, ExamStatus

def create_exam(db: Session, exam: ExamCreate, instructor_id: int) -> Exam:
    """Créer un nouvel examen"""
    db_exam = Exam(
        title=exam.title,
        description=exam.description,
        duration_minutes=exam.duration_minutes,
        instructions=exam.instructions,
        status=exam.status.value,
        start_time=exam.start_time,
        end_time=exam.end_time,
        instructor_id=instructor_id,
        allowed_apps=json.dumps(exam.allowed_apps) if exam.allowed_apps else None,
        allowed_domains=json.dumps(exam.allowed_domains) if exam.allowed_domains else None,
        is_active=True
    )
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def get_exam(db: Session, exam_id: int) -> Optional[Exam]:
    """Récupérer un examen par son ID"""
    return db.query(Exam).filter(Exam.id == exam_id).first()

def get_exams(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    instructor_id: Optional[int] = None,
    status: Optional[ExamStatus] = None
) -> List[Exam]:
    """Récupérer la liste des examens avec filtres"""
    query = db.query(Exam).filter(Exam.is_active == True)
    
    if instructor_id:
        query = query.filter(Exam.instructor_id == instructor_id)
    
    if status:
        query = query.filter(Exam.status == status.value)
    
    return query.offset(skip).limit(limit).all()

def update_exam(db: Session, exam_id: int, exam_update: ExamUpdate) -> Optional[Exam]:
    """Mettre à jour un examen"""
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        return None
    
    update_data = exam_update.dict(exclude_unset=True)
    
    # Convertir les listes en JSON strings pour les champs allowed_apps et allowed_domains
    if "allowed_apps" in update_data and update_data["allowed_apps"] is not None:
        update_data["allowed_apps"] = json.dumps(update_data["allowed_apps"])
    
    if "allowed_domains" in update_data and update_data["allowed_domains"] is not None:
        update_data["allowed_domains"] = json.dumps(update_data["allowed_domains"])
    
    # Convertir le statut en string si c'est un enum
    if "status" in update_data and isinstance(update_data["status"], ExamStatus):
        update_data["status"] = update_data["status"].value
    
    for field, value in update_data.items():
        setattr(db_exam, field, value)
    
    db_exam.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exam)
    return db_exam

def delete_exam(db: Session, exam_id: int) -> bool:
    """Supprimer un examen (soft delete)"""
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        return False
    
    db_exam.is_active = False
    db_exam.updated_at = datetime.utcnow()
    db.commit()
    return True

def update_exam_pdf(db: Session, exam_id: int, pdf_path: str) -> Optional[Exam]:
    """Mettre à jour le chemin du fichier PDF d'un examen"""
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        return None
    
    db_exam.pdf_path = pdf_path
    db_exam.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_exam)
    return db_exam

def get_exam_count(db: Session, instructor_id: Optional[int] = None) -> int:
    """Compter le nombre total d'examens"""
    query = db.query(Exam).filter(Exam.is_active == True)
    
    if instructor_id:
        query = query.filter(Exam.instructor_id == instructor_id)
    
    return query.count()
