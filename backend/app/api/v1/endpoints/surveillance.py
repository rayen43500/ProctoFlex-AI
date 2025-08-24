"""
Endpoints de surveillance ProctoFlex AI
Reconnaissance faciale et gestion des sessions
"""

import base64
import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db, User, ExamSession, SecurityAlert
from app.core.security import get_current_user
from app.ai.face_recognition import FaceRecognitionEngine
from app.models.surveillance import (
    FaceVerificationRequest,
    FaceVerificationResponse,
    SessionStartRequest,
    SessionStatusResponse
)

router = APIRouter()

# Initialisation du moteur de reconnaissance faciale
face_engine = FaceRecognitionEngine()

@router.post("/verify-identity", response_model=FaceVerificationResponse)
async def verify_identity(
    request: FaceVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vérifie l'identité d'un étudiant par reconnaissance faciale
    """
    try:
        # Décodage des images base64
        reference_image_data = base64.b64decode(request.reference_image.split(',')[1])
        current_image_data = base64.b64decode(request.current_image.split(',')[1])
        
        # Conversion en numpy arrays
        reference_np = np.frombuffer(reference_image_data, np.uint8)
        current_np = np.frombuffer(current_image_data, np.uint8)
        
        reference_image = cv2.imdecode(reference_np, cv2.IMREAD_COLOR)
        current_image = cv2.imdecode(current_np, cv2.IMREAD_COLOR)
        
        # Vérification de l'identité
        verification_result = face_engine.verify_identity(reference_image, current_image)
        
        # Enregistrement de l'alerte si échec
        if not verification_result['verified']:
            alert = SecurityAlert(
                session_id=request.session_id,
                alert_type="face_verification_failed",
                severity="high",
                description=f"Échec de vérification d'identité: {verification_result.get('error', 'Confiance insuffisante')}"
            )
            db.add(alert)
            db.commit()
        
        return FaceVerificationResponse(
            verified=verification_result['verified'],
            confidence=verification_result['confidence'],
            message="Vérification d'identité réussie" if verification_result['verified'] else "Vérification d'identité échouée"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")

@router.post("/start-session", response_model=SessionStatusResponse)
async def start_exam_session(
    request: SessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Démarre une session d'examen avec vérification d'identité
    """
    try:
        # Vérification que l'utilisateur est un étudiant
        if current_user.role != "student":
            raise HTTPException(status_code=403, detail="Seuls les étudiants peuvent démarrer des sessions d'examen")
        
        # Vérification de l'identité
        if not request.identity_verified:
            raise HTTPException(status_code=400, detail="L'identité doit être vérifiée avant de démarrer la session")
        
        # Création de la session
        session = ExamSession(
            exam_id=request.exam_id,
            student_id=current_user.id,
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return SessionStatusResponse(
            session_id=session.id,
            status="active",
            message="Session d'examen démarrée avec succès"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du démarrage de la session: {str(e)}")

@router.get("/session/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère le statut d'une session d'examen
    """
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Vérification des permissions
    if current_user.role == "student" and session.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette session")
    
    return SessionStatusResponse(
        session_id=session.id,
        status=session.status,
        message=f"Session {session.status}"
    )

@router.post("/session/{session_id}/end")
async def end_exam_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Termine une session d'examen
    """
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Vérification des permissions
    if current_user.role == "student" and session.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette session")
    
    # Mise à jour du statut
    session.status = "completed"
    db.commit()
    
    return {"message": "Session terminée avec succès"}

@router.get("/session/{session_id}/alerts")
async def get_session_alerts(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les alertes de sécurité d'une session
    """
    session = db.query(ExamSession).filter(ExamSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session non trouvée")
    
    # Vérification des permissions
    if current_user.role == "student" and session.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé à cette session")
    
    alerts = db.query(SecurityAlert).filter(SecurityAlert.session_id == session_id).all()
    
    return [
        {
            "id": alert.id,
            "type": alert.alert_type,
            "severity": alert.severity,
            "description": alert.description,
            "timestamp": alert.timestamp,
            "resolved": alert.is_resolved
        }
        for alert in alerts
    ]

@router.post("/analyze-face")
async def analyze_face_behavior(
    image_data: str,
    current_user: User = Depends(get_current_user)
):
    """
    Analyse le comportement du visage en temps réel
    """
    try:
        # Décodage de l'image
        image_data_clean = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data_clean)
        image_np = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        
        # Analyse du comportement
        analysis = face_engine.analyze_face_behavior(image)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")
