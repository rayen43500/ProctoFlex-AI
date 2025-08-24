"""
Modèles Pydantic pour la surveillance ProctoFlex AI
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FaceVerificationRequest(BaseModel):
    """Requête de vérification d'identité par reconnaissance faciale"""
    reference_image: str  # Image de référence (pièce d'identité) en base64
    current_image: str    # Image actuelle (webcam) en base64
    session_id: Optional[int] = None

class FaceVerificationResponse(BaseModel):
    """Réponse de vérification d'identité"""
    verified: bool
    confidence: float
    message: str

class SessionStartRequest(BaseModel):
    """Requête de démarrage de session d'examen"""
    exam_id: int
    identity_verified: bool

class SessionStatusResponse(BaseModel):
    """Statut d'une session d'examen"""
    session_id: int
    status: str
    message: str

class SecurityAlertResponse(BaseModel):
    """Alerte de sécurité"""
    id: int
    type: str
    severity: str
    description: str
    timestamp: datetime
    resolved: bool

class ProcessInfo(BaseModel):
    """Informations sur un processus système"""
    process_name: str
    process_id: int
    cpu_usage: float
    memory_usage: Optional[float] = None

class ApplicationWhitelist(BaseModel):
    """Liste blanche d'applications autorisées"""
    exam_id: int
    allowed_processes: list[str]
    allowed_domains: Optional[list[str]] = None

class FaceAnalysisResult(BaseModel):
    """Résultat de l'analyse faciale en temps réel"""
    face_detected: bool
    multiple_faces: bool
    face_visible: bool
    confidence: float
    face_count: Optional[int] = None
    error: Optional[str] = None
