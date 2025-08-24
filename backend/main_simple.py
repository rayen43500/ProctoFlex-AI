"""
ProctoFlex AI - Backend API (Version Simplifiée)
Serveur FastAPI pour la surveillance d'examens en ligne
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Configuration de l'application FastAPI
app = FastAPI(
    title="ProctoFlex AI API",
    description="API de surveillance intelligente pour examens en ligne",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route de santé
@app.get("/health")
async def health_check():
    """Vérification de l'état du serveur"""
    return {
        "status": "healthy",
        "service": "ProctoFlex AI Backend",
        "version": "1.0.0",
        "message": "Serveur démarré avec succès !"
    }

# Route racine
@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue sur ProctoFlex AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Route de test
@app.get("/test")
async def test():
    """Route de test simple"""
    return {
        "message": "Test réussi !",
        "config": {
            "host": settings.HOST,
            "port": settings.PORT,
            "debug": settings.DEBUG
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
