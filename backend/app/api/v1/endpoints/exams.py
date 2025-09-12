"""
Endpoints API pour la gestion des examens
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import json
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.exam import Exam, ExamCreate, ExamUpdate, ExamList, ExamStatus
from app.crud import exam as exam_crud

router = APIRouter()

# Configuration pour le stockage des fichiers
UPLOAD_DIR = "uploads/exams"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=Exam)
async def create_exam(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    duration_minutes: int = Form(...),
    instructions: Optional[str] = Form(None),
    status: str = Form("draft"),
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None),
    allowed_apps: Optional[str] = Form(None),
    allowed_domains: Optional[str] = Form(None),
    pdf_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouvel examen"""
    
    # Vérifier que l'utilisateur est un instructeur ou admin
    if current_user.role not in ["instructor", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Seuls les instructeurs et administrateurs peuvent créer des examens"
        )
    
    # Traiter les données du formulaire
    exam_data = ExamCreate(
        title=title,
        description=description,
        duration_minutes=duration_minutes,
        instructions=instructions,
        status=ExamStatus(status),
        start_time=datetime.fromisoformat(start_time) if start_time else None,
        end_time=datetime.fromisoformat(end_time) if end_time else None,
        allowed_apps=json.loads(allowed_apps) if allowed_apps else [],
        allowed_domains=json.loads(allowed_domains) if allowed_domains else []
    )
    
    # Créer l'examen
    db_exam = exam_crud.create_exam(db, exam_data, current_user.id)
    
    # Traiter le fichier PDF si fourni
    if pdf_file and pdf_file.filename:
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Seuls les fichiers PDF sont autorisés"
            )
        
        # Générer un nom de fichier unique
        file_extension = os.path.splitext(pdf_file.filename)[1]
        unique_filename = f"{db_exam.id}_{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Sauvegarder le fichier
        try:
            with open(file_path, "wb") as buffer:
                content = await pdf_file.read()
                buffer.write(content)
            
            # Mettre à jour l'examen avec le chemin du fichier
            exam_crud.update_exam_pdf(db, db_exam.id, file_path)
            db_exam.pdf_path = file_path
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la sauvegarde du fichier: {str(e)}"
            )
    
    # Convertir les données JSON en listes pour la réponse
    if db_exam.allowed_apps:
        db_exam.allowed_apps = json.loads(db_exam.allowed_apps)
    if db_exam.allowed_domains:
        db_exam.allowed_domains = json.loads(db_exam.allowed_domains)
    
    return db_exam

@router.get("/", response_model=ExamList)
async def get_exams(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer la liste des examens"""
    
    # Filtrer par instructeur si l'utilisateur n'est pas admin
    instructor_id = None if current_user.role == "admin" else current_user.id
    
    # Convertir le statut en enum si fourni
    exam_status = ExamStatus(status) if status else None
    
    exams = exam_crud.get_exams(
        db, 
        skip=skip, 
        limit=limit, 
        instructor_id=instructor_id,
        status=exam_status
    )
    
    # Convertir les données JSON en listes
    for exam in exams:
        if exam.allowed_apps:
            exam.allowed_apps = json.loads(exam.allowed_apps)
        if exam.allowed_domains:
            exam.allowed_domains = json.loads(exam.allowed_domains)
    
    total = exam_crud.get_exam_count(db, instructor_id)
    
    return ExamList(
        exams=exams,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@router.get("/{exam_id}", response_model=Exam)
async def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer un examen par son ID"""
    
    exam = exam_crud.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    # Vérifier les permissions
    if current_user.role not in ["admin"] and exam.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas l'autorisation d'accéder à cet examen"
        )
    
    # Convertir les données JSON en listes
    if exam.allowed_apps:
        exam.allowed_apps = json.loads(exam.allowed_apps)
    if exam.allowed_domains:
        exam.allowed_domains = json.loads(exam.allowed_domains)
    
    return exam

@router.put("/{exam_id}", response_model=Exam)
async def update_exam(
    exam_id: int,
    exam_update: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mettre à jour un examen"""
    
    # Vérifier que l'examen existe
    exam = exam_crud.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    # Vérifier les permissions
    if current_user.role not in ["admin"] and exam.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas l'autorisation de modifier cet examen"
        )
    
    updated_exam = exam_crud.update_exam(db, exam_id, exam_update)
    if not updated_exam:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    # Convertir les données JSON en listes
    if updated_exam.allowed_apps:
        updated_exam.allowed_apps = json.loads(updated_exam.allowed_apps)
    if updated_exam.allowed_domains:
        updated_exam.allowed_domains = json.loads(updated_exam.allowed_domains)
    
    return updated_exam

@router.delete("/{exam_id}")
async def delete_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer un examen"""
    
    # Vérifier que l'examen existe
    exam = exam_crud.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    # Vérifier les permissions
    if current_user.role not in ["admin"] and exam.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas l'autorisation de supprimer cet examen"
        )
    
    success = exam_crud.delete_exam(db, exam_id)
    if not success:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    return {"message": "Examen supprimé avec succès"}

@router.post("/{exam_id}/pdf")
async def upload_exam_pdf(
    exam_id: int,
    pdf_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Télécharger un fichier PDF pour un examen"""
    
    # Vérifier que l'examen existe
    exam = exam_crud.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    # Vérifier les permissions
    if current_user.role not in ["admin"] and exam.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas l'autorisation de modifier cet examen"
        )
    
    # Vérifier le type de fichier
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Seuls les fichiers PDF sont autorisés"
        )
    
    # Générer un nom de fichier unique
    file_extension = os.path.splitext(pdf_file.filename)[1]
    unique_filename = f"{exam_id}_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Supprimer l'ancien fichier s'il existe
    if exam.pdf_path and os.path.exists(exam.pdf_path):
        try:
            os.remove(exam.pdf_path)
        except Exception:
            pass  # Ignorer les erreurs de suppression
    
    # Sauvegarder le nouveau fichier
    try:
        with open(file_path, "wb") as buffer:
            content = await pdf_file.read()
            buffer.write(content)
        
        # Mettre à jour l'examen avec le nouveau chemin
        updated_exam = exam_crud.update_exam_pdf(db, exam_id, file_path)
        return {"message": "Fichier PDF téléchargé avec succès", "file_path": file_path}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la sauvegarde du fichier: {str(e)}"
        )

@router.get("/{exam_id}/pdf")
async def download_exam_pdf(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Télécharger le fichier PDF d'un examen"""
    
    # Vérifier que l'examen existe
    exam = exam_crud.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Examen non trouvé")
    
    # Vérifier les permissions
    if current_user.role not in ["admin"] and exam.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Vous n'avez pas l'autorisation d'accéder à ce fichier"
        )
    
    # Vérifier que le fichier existe
    if not exam.pdf_path or not os.path.exists(exam.pdf_path):
        raise HTTPException(status_code=404, detail="Fichier PDF non trouvé")
    
    # Retourner le fichier
    return FileResponse(
        path=exam.pdf_path,
        media_type='application/pdf',
        filename=f"exam_{exam_id}.pdf"
    )