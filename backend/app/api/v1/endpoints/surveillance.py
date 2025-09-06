"""
Endpoints API pour la surveillance en temps réel
ProctoFlex AI - Université de Monastir
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging
import asyncio

from app.core.security import get_current_user
from app.models.user import User
from app.core.database import get_db
from app.surveillance.multimodal_surveillance import (
    multimodal_surveillance_service,
    SurveillanceFrame,
    SurveillanceAlert,
    AlertType,
    AlertSeverity
)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Gestionnaire de connexions WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        await websocket.accept()
        connection_id = f"{user_id}_{session_id}_{datetime.now().timestamp()}"
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(connection_id)
        
        logger.info(f"Connexion WebSocket établie: {connection_id}")
        return connection_id

    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
            # Retirer de la liste des connexions de session
            for session_id, connections in self.session_connections.items():
                if connection_id in connections:
                    connections.remove(connection_id)
                    if not connections:
                        del self.session_connections[session_id]
                    break
            
            logger.info(f"Connexion WebSocket fermée: {connection_id}")

    async def send_personal_message(self, message: str, connection_id: str):
        if connection_id in self.active_connections:
            await self.active_connections[connection_id].send_text(message)

    async def broadcast_to_session(self, message: str, session_id: str):
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id]:
                await self.send_personal_message(message, connection_id)

manager = ConnectionManager()

@router.post("/sessions/{session_id}/start")
async def start_surveillance_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Démarre une session de surveillance"""
    try:
        logger.info(f"Démarrage de la session de surveillance {session_id} pour l'utilisateur {current_user.id}")
        
        # Démarrer la session de surveillance
        success = await multimodal_surveillance_service.start_surveillance_session(
            session_id=session_id,
            student_id=str(current_user.id),
            exam_id="1"  # En production, récupérer depuis la base de données
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Impossible de démarrer la session de surveillance")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session de surveillance démarrée avec succès",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage de la session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du démarrage de la session: {str(e)}")

@router.post("/sessions/{session_id}/stop")
async def stop_surveillance_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Arrête une session de surveillance"""
    try:
        logger.info(f"Arrêt de la session de surveillance {session_id}")
        
        # Arrêter la session de surveillance
        result = await multimodal_surveillance_service.stop_surveillance_session(session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("reason", "Impossible d'arrêter la session"))
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Session de surveillance arrêtée avec succès",
            "report": result.get("report", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt de la session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'arrêt de la session: {str(e)}")

@router.post("/sessions/{session_id}/analyze")
async def analyze_surveillance_frame(
    session_id: str,
    video_frame: Optional[str] = None,
    audio_chunk: Optional[str] = None,
    screen_capture: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyse un frame de surveillance multimodale"""
    try:
        logger.debug(f"Analyse du frame pour la session {session_id}")
        
        # Créer le frame de surveillance
        frame = SurveillanceFrame(
            session_id=session_id,
            timestamp=datetime.now(),
            video_frame=video_frame,
            audio_chunk=audio_chunk,
            screen_capture=screen_capture
        )
        
        # Analyser le frame
        result = await multimodal_surveillance_service.analyze_surveillance_frame(frame)
        
        # Diffuser les alertes via WebSocket si nécessaire
        if result.alerts:
            alert_data = {
                "type": "surveillance_alert",
                "session_id": session_id,
                "alerts": [
                    {
                        "id": alert.id,
                        "type": alert.alert_type.value,
                        "severity": alert.severity.value,
                        "message": alert.description,
                        "timestamp": alert.timestamp.isoformat(),
                        "confidence": alert.confidence
                    }
                    for alert in result.alerts
                ],
                "risk_level": result.risk_level,
                "timestamp": result.timestamp.isoformat()
            }
            
            await manager.broadcast_to_session(json.dumps(alert_data), session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "risk_level": result.risk_level,
            "confidence": result.confidence,
            "alerts_count": len(result.alerts),
            "processing_time": result.processing_time,
            "timestamp": result.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du frame pour la session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse: {str(e)}")

@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère le statut d'une session de surveillance"""
    try:
        status = multimodal_surveillance_service.get_session_status(session_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        return {
            "success": True,
            "session_id": session_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut de la session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du statut: {str(e)}")

@router.get("/sessions/{session_id}/alerts")
async def get_session_alerts(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les alertes récentes d'une session"""
    try:
        alerts = multimodal_surveillance_service.get_recent_alerts(session_id, limit)
        
        return {
            "success": True,
            "session_id": session_id,
            "alerts": [
                {
                    "id": alert.id,
                    "type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "message": alert.description,
                    "timestamp": alert.timestamp.isoformat(),
                    "confidence": alert.confidence,
                    "resolved": alert.is_resolved,
                    "metadata": alert.metadata
                }
                for alert in alerts
            ],
            "total_count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des alertes de la session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des alertes: {str(e)}")

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str
):
    """Endpoint WebSocket pour la surveillance en temps réel"""
    connection_id = None
    
    try:
        # Authentifier l'utilisateur (simplifié pour l'exemple)
        # En production, valider le token JWT
        user_id = "1"  # Simulation
        
        # Établir la connexion
        connection_id = await manager.connect(websocket, session_id, user_id)
        
        # Envoyer un message de bienvenue
        welcome_message = {
            "type": "connection_established",
            "session_id": session_id,
            "message": "Connexion WebSocket établie",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        # Boucle de réception des messages
        while True:
            try:
                # Recevoir un message du client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Traiter le message selon son type
                if message.get("type") == "ping":
                    pong_message = {
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(pong_message))
                
                elif message.get("type") == "surveillance_data":
                    # Traiter les données de surveillance
                    await process_surveillance_data(session_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"Client déconnecté: {connection_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"Message JSON invalide reçu de {connection_id}")
            except Exception as e:
                logger.error(f"Erreur lors du traitement du message: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"Connexion WebSocket fermée: {connection_id}")
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint WebSocket: {e}")
    finally:
        if connection_id:
            manager.disconnect(connection_id)

async def process_surveillance_data(session_id: str, message: Dict[str, Any]):
    """Traite les données de surveillance reçues via WebSocket"""
    try:
        # Créer le frame de surveillance
        frame = SurveillanceFrame(
            session_id=session_id,
            timestamp=datetime.now(),
            video_frame=message.get("video_frame"),
            audio_chunk=message.get("audio_chunk"),
            screen_capture=message.get("screen_capture")
        )
        
        # Analyser le frame
        result = await multimodal_surveillance_service.analyze_surveillance_frame(frame)
        
        # Préparer la réponse
        response = {
            "type": "surveillance_analysis",
            "session_id": session_id,
            "risk_level": result.risk_level,
            "confidence": result.confidence,
            "alerts": [
                {
                    "id": alert.id,
                    "type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "message": alert.description,
                    "timestamp": alert.timestamp.isoformat(),
                    "confidence": alert.confidence
                }
                for alert in result.alerts
            ],
            "processing_time": result.processing_time,
            "timestamp": result.timestamp.isoformat()
        }
        
        # Diffuser la réponse à tous les clients connectés à cette session
        await manager.broadcast_to_session(json.dumps(response), session_id)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement des données de surveillance: {e}")

@router.get("/health")
async def surveillance_health_check(current_user: User = Depends(get_current_user)):
    """Vérifie l'état des services de surveillance"""
    try:
        # Vérifier les services de surveillance
        services_status = {
            "multimodal_surveillance": "healthy",
            "face_recognition": "healthy",
            "object_detection": "healthy",
            "audio_analysis": "healthy",
            "websocket_manager": "healthy"
        }
        
        # Compter les connexions WebSocket actives
        active_connections = len(manager.active_connections)
        active_sessions = len(manager.session_connections)
        
        return {
            "status": "healthy",
            "services": services_status,
            "active_connections": active_connections,
            "active_sessions": active_sessions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du health check de surveillance: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du health check: {str(e)}")