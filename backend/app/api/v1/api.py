"""
Routeur principal de l'API ProctoFlex AI
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, exams, sessions, surveillance, users

# Création du routeur principal
api_router = APIRouter()

# Inclusion des sous-routeurs
api_router.include_router(auth.router, prefix="/auth", tags=["authentification"])
api_router.include_router(users.router, prefix="/users", tags=["utilisateurs"])
api_router.include_router(exams.router, prefix="/exams", tags=["examens"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(surveillance.router, prefix="/surveillance", tags=["surveillance"])
