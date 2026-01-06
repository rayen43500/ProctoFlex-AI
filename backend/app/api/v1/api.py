"""
Routeur principal de l'API ProctoFlex AI
"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, surveillance

# Création du routeur principal
api_router = APIRouter()

# Inclusion des sous-routeurs (seulement les modules existants)
api_router.include_router(auth.router, prefix="/auth", tags=["authentification"])
api_router.include_router(surveillance.router, prefix="/surveillance", tags=["surveillance"])

# TODO: Ajouter les routeurs suivants quand les fichiers seront créés:
# - users.router (prefix="/users", tags=["utilisateurs"])
# - exams.router (prefix="/exams", tags=["examens"])
# - sessions.router (prefix="/sessions", tags=["sessions"])
