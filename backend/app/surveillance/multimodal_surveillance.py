"""
Module de surveillance multimodale en temps réel
ProctoFlex AI - Université de Monastir
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import time
import json
from datetime import datetime

from app.ai.face_recognition.identity_verification import identity_verification_service
from app.ai.object_detection import object_detection_service
from app.ai.face_detection import face_detection_service

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(Enum):
    FACE_NOT_DETECTED = "face_not_detected"
    MULTIPLE_FACES = "multiple_faces"
    GAZE_AWAY = "gaze_away"
    SUSPICIOUS_OBJECTS = "suspicious_objects"
    VOICE_DETECTED = "voice_detected"
    SUSPICIOUS_AUDIO = "suspicious_audio"
    UNAUTHORIZED_WINDOW = "unauthorized_window"
    COPY_PASTE_ACTIVITY = "copy_paste_activity"
    APPLICATION_SWITCH = "application_switch"

@dataclass
class SurveillanceAlert:
    """Alerte de surveillance"""
    id: str
    session_id: str
    alert_type: AlertType
    severity: AlertSeverity
    timestamp: datetime
    description: str
    confidence: float
    metadata: Dict[str, Any]
    is_resolved: bool = False

@dataclass
class SurveillanceFrame:
    """Frame de surveillance multimodale"""
    session_id: str
    timestamp: datetime
    video_frame: Optional[str] = None  # base64
    audio_chunk: Optional[str] = None  # base64
    screen_capture: Optional[str] = None  # base64
    system_info: Optional[Dict[str, Any]] = None

@dataclass
class SurveillanceResult:
    """Résultat de l'analyse de surveillance"""
    session_id: str
    timestamp: datetime
    alerts: List[SurveillanceAlert]
    risk_level: str
    confidence: float
    processing_time: float
    analysis_summary: Dict[str, Any]

class MultimodalSurveillanceService:
    """Service de surveillance multimodale en temps réel"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.alert_history: List[SurveillanceAlert] = []
        self.max_alerts_per_session = 1000
        
        # Seuils de détection
        self.thresholds = {
            "face_confidence": 0.8,
            "object_confidence": 0.7,
            "audio_threshold": 0.5,
            "gaze_threshold": 0.6
        }
        
        # Configuration des alertes
        self.alert_config = {
            AlertType.FACE_NOT_DETECTED: {"severity": AlertSeverity.MEDIUM, "threshold": 0.8},
            AlertType.MULTIPLE_FACES: {"severity": AlertSeverity.HIGH, "threshold": 0.9},
            AlertType.GAZE_AWAY: {"severity": AlertSeverity.MEDIUM, "threshold": 0.7},
            AlertType.SUSPICIOUS_OBJECTS: {"severity": AlertSeverity.HIGH, "threshold": 0.8},
            AlertType.VOICE_DETECTED: {"severity": AlertSeverity.MEDIUM, "threshold": 0.6},
            AlertType.SUSPICIOUS_AUDIO: {"severity": AlertSeverity.HIGH, "threshold": 0.7},
            AlertType.UNAUTHORIZED_WINDOW: {"severity": AlertSeverity.CRITICAL, "threshold": 0.9},
            AlertType.COPY_PASTE_ACTIVITY: {"severity": AlertSeverity.MEDIUM, "threshold": 0.5},
            AlertType.APPLICATION_SWITCH: {"severity": AlertSeverity.MEDIUM, "threshold": 0.6}
        }
    
    async def start_surveillance_session(self, session_id: str, student_id: str, exam_id: str) -> bool:
        """Démarre une session de surveillance"""
        try:
            logger.info(f"Démarrage de la session de surveillance {session_id}")
            
            self.active_sessions[session_id] = {
                "student_id": student_id,
                "exam_id": exam_id,
                "start_time": datetime.now(),
                "last_activity": datetime.now(),
                "alert_count": 0,
                "risk_level": "low",
                "status": "active"
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la session {session_id}: {e}")
            return False
    
    async def stop_surveillance_session(self, session_id: str) -> Dict[str, Any]:
        """Arrête une session de surveillance"""
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "reason": "Session non trouvée"}
            
            session_data = self.active_sessions[session_id]
            session_data["status"] = "stopped"
            session_data["end_time"] = datetime.now()
            
            # Générer le rapport final
            report = await self._generate_session_report(session_id)
            
            # Nettoyer la session
            del self.active_sessions[session_id]
            
            logger.info(f"Session de surveillance {session_id} arrêtée")
            
            return {
                "success": True,
                "session_id": session_id,
                "duration": (session_data["end_time"] - session_data["start_time"]).total_seconds(),
                "total_alerts": session_data["alert_count"],
                "final_risk_level": session_data["risk_level"],
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de la session {session_id}: {e}")
            return {"success": False, "reason": str(e)}
    
    async def analyze_surveillance_frame(self, frame: SurveillanceFrame) -> SurveillanceResult:
        """Analyse un frame de surveillance multimodale"""
        start_time = time.time()
        
        try:
            logger.debug(f"Analyse du frame pour la session {frame.session_id}")
            
            alerts = []
            analysis_summary = {
                "face_analysis": {},
                "object_analysis": {},
                "audio_analysis": {},
                "screen_analysis": {}
            }
            
            # Analyser la vidéo si disponible
            if frame.video_frame:
                face_alerts, face_summary = await self._analyze_video_frame(frame)
                alerts.extend(face_alerts)
                analysis_summary["face_analysis"] = face_summary
            
            # Analyser l'audio si disponible
            if frame.audio_chunk:
                audio_alerts, audio_summary = await self._analyze_audio_chunk(frame)
                alerts.extend(audio_alerts)
                analysis_summary["audio_analysis"] = audio_summary
            
            # Analyser l'écran si disponible
            if frame.screen_capture:
                screen_alerts, screen_summary = await self._analyze_screen_capture(frame)
                alerts.extend(screen_alerts)
                analysis_summary["screen_analysis"] = screen_summary
            
            # Calculer le niveau de risque global
            risk_level = self._calculate_risk_level(alerts)
            
            # Mettre à jour la session
            if frame.session_id in self.active_sessions:
                self.active_sessions[frame.session_id]["last_activity"] = frame.timestamp
                self.active_sessions[frame.session_id]["risk_level"] = risk_level
                self.active_sessions[frame.session_id]["alert_count"] += len(alerts)
            
            # Ajouter les alertes à l'historique
            self.alert_history.extend(alerts)
            
            # Limiter l'historique des alertes
            if len(self.alert_history) > self.max_alerts_per_session * 10:
                self.alert_history = self.alert_history[-self.max_alerts_per_session * 10:]
            
            processing_time = time.time() - start_time
            
            return SurveillanceResult(
                session_id=frame.session_id,
                timestamp=frame.timestamp,
                alerts=alerts,
                risk_level=risk_level,
                confidence=self._calculate_overall_confidence(alerts),
                processing_time=processing_time,
                analysis_summary=analysis_summary
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du frame: {e}")
            return SurveillanceResult(
                session_id=frame.session_id,
                timestamp=frame.timestamp,
                alerts=[],
                risk_level="unknown",
                confidence=0.0,
                processing_time=time.time() - start_time,
                analysis_summary={"error": str(e)}
            )
    
    async def _analyze_video_frame(self, frame: SurveillanceFrame) -> tuple[List[SurveillanceAlert], Dict[str, Any]]:
        """Analyse une frame vidéo"""
        alerts = []
        summary = {}
        
        try:
            # Détecter les visages
            faces = face_detection_service.detect_faces(frame.video_frame)
            summary["faces_detected"] = len(faces)
            
            # Vérifier la présence de visage
            if len(faces) == 0:
                alert = SurveillanceAlert(
                    id=f"{frame.session_id}_{int(time.time())}_face_not_detected",
                    session_id=frame.session_id,
                    alert_type=AlertType.FACE_NOT_DETECTED,
                    severity=AlertSeverity.MEDIUM,
                    timestamp=frame.timestamp,
                    description="Aucun visage détecté",
                    confidence=0.9,
                    metadata={"frame_type": "video"}
                )
                alerts.append(alert)
            
            # Vérifier les visages multiples
            elif len(faces) > 1:
                alert = SurveillanceAlert(
                    id=f"{frame.session_id}_{int(time.time())}_multiple_faces",
                    session_id=frame.session_id,
                    alert_type=AlertType.MULTIPLE_FACES,
                    severity=AlertSeverity.HIGH,
                    timestamp=frame.timestamp,
                    description=f"{len(faces)} visages détectés",
                    confidence=0.95,
                    metadata={"face_count": len(faces)}
                )
                alerts.append(alert)
            
            # Analyser le regard si un visage est détecté
            if len(faces) == 1:
                gaze_analysis = face_detection_service.track_gaze(frame.video_frame, faces[0])
                summary["gaze_analysis"] = gaze_analysis
                
                if not gaze_analysis.get("looking_at_screen", True):
                    alert = SurveillanceAlert(
                        id=f"{frame.session_id}_{int(time.time())}_gaze_away",
                        session_id=frame.session_id,
                        alert_type=AlertType.GAZE_AWAY,
                        severity=AlertSeverity.MEDIUM,
                        timestamp=frame.timestamp,
                        description="Regard détourné de l'écran",
                        confidence=gaze_analysis.get("confidence", 0.7),
                        metadata=gaze_analysis
                    )
                    alerts.append(alert)
            
            # Détecter les objets suspects
            object_result = object_detection_service.detect_suspicious_objects(frame.video_frame)
            summary["object_analysis"] = object_result
            
            if object_result["objects_detected"] > 0:
                severity = AlertSeverity.HIGH if object_result["alert_level"] == "critical" else AlertSeverity.MEDIUM
                alert = SurveillanceAlert(
                    id=f"{frame.session_id}_{int(time.time())}_suspicious_objects",
                    session_id=frame.session_id,
                    alert_type=AlertType.SUSPICIOUS_OBJECTS,
                    severity=severity,
                    timestamp=frame.timestamp,
                    description=f"Objets suspects détectés: {object_result['objects_detected']}",
                    confidence=object_result.get("confidence", 0.8),
                    metadata=object_result
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse vidéo: {e}")
            summary["error"] = str(e)
        
        return alerts, summary
    
    async def _analyze_audio_chunk(self, frame: SurveillanceFrame) -> tuple[List[SurveillanceAlert], Dict[str, Any]]:
        """Analyse un chunk audio"""
        alerts = []
        summary = {}
        
        try:
            # Simulation de l'analyse audio
            # En production, utiliser des bibliothèques d'analyse audio réelles
            
            # Décoder les données audio
            import base64
            audio_data = frame.audio_chunk
            if ',' in audio_data:
                audio_data = audio_data.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_data)
            data_length = len(audio_bytes)
            
            # Simulation de l'analyse
            noise_level = min(1.0, data_length / 10000)
            voice_detected = noise_level > 0.3
            
            summary = {
                "noise_level": noise_level,
                "voice_detected": voice_detected,
                "data_size": data_length
            }
            
            # Détecter la voix
            if voice_detected:
                alert = SurveillanceAlert(
                    id=f"{frame.session_id}_{int(time.time())}_voice_detected",
                    session_id=frame.session_id,
                    alert_type=AlertType.VOICE_DETECTED,
                    severity=AlertSeverity.MEDIUM,
                    timestamp=frame.timestamp,
                    description="Voix détectée",
                    confidence=noise_level,
                    metadata={"noise_level": noise_level}
                )
                alerts.append(alert)
            
            # Détecter les sons suspects (simulation)
            import random
            if random.random() < 0.1:  # 10% de chance
                alert = SurveillanceAlert(
                    id=f"{frame.session_id}_{int(time.time())}_suspicious_audio",
                    session_id=frame.session_id,
                    alert_type=AlertType.SUSPICIOUS_AUDIO,
                    severity=AlertSeverity.HIGH,
                    timestamp=frame.timestamp,
                    description="Sons suspects détectés",
                    confidence=0.8,
                    metadata={"audio_analysis": "suspicious_pattern"}
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse audio: {e}")
            summary["error"] = str(e)
        
        return alerts, summary
    
    async def _analyze_screen_capture(self, frame: SurveillanceFrame) -> tuple[List[SurveillanceAlert], Dict[str, Any]]:
        """Analyse une capture d'écran"""
        alerts = []
        summary = {}
        
        try:
            # Simulation de l'analyse d'écran
            # En production, analyser les fenêtres ouvertes, les applications actives, etc.
            
            summary = {
                "screen_analyzed": True,
                "timestamp": frame.timestamp.isoformat()
            }
            
            # Simuler la détection d'activités suspectes
            import random
            
            # Détecter les fenêtres non autorisées (simulation)
            if random.random() < 0.05:  # 5% de chance
                alert = SurveillanceAlert(
                    id=f"{frame.session_id}_{int(time.time())}_unauthorized_window",
                    session_id=frame.session_id,
                    alert_type=AlertType.UNAUTHORIZED_WINDOW,
                    severity=AlertSeverity.CRITICAL,
                    timestamp=frame.timestamp,
                    description="Fenêtre non autorisée détectée",
                    confidence=0.9,
                    metadata={"window_title": "Suspicious App"}
                )
                alerts.append(alert)
            
            # Détecter l'activité copier-coller (simulation)
            if random.random() < 0.1:  # 10% de chance
                alert = SurveillanceAlert(
                    id=f"{frame.session_id}_{int(time.time())}_copy_paste",
                    session_id=frame.session_id,
                    alert_type=AlertType.COPY_PASTE_ACTIVITY,
                    severity=AlertSeverity.MEDIUM,
                    timestamp=frame.timestamp,
                    description="Activité copier-coller détectée",
                    confidence=0.7,
                    metadata={"activity_type": "copy_paste"}
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse d'écran: {e}")
            summary["error"] = str(e)
        
        return alerts, summary
    
    def _calculate_risk_level(self, alerts: List[SurveillanceAlert]) -> str:
        """Calcule le niveau de risque global basé sur les alertes"""
        if not alerts:
            return "low"
        
        # Calculer le score de risque
        risk_scores = {
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4
        }
        
        total_score = sum(risk_scores[alert.severity] for alert in alerts)
        avg_score = total_score / len(alerts)
        
        if avg_score >= 3.5:
            return "critical"
        elif avg_score >= 2.5:
            return "high"
        elif avg_score >= 1.5:
            return "medium"
        else:
            return "low"
    
    def _calculate_overall_confidence(self, alerts: List[SurveillanceAlert]) -> float:
        """Calcule la confiance globale de l'analyse"""
        if not alerts:
            return 1.0
        
        total_confidence = sum(alert.confidence for alert in alerts)
        return total_confidence / len(alerts)
    
    async def _generate_session_report(self, session_id: str) -> Dict[str, Any]:
        """Génère un rapport de session"""
        try:
            # Filtrer les alertes pour cette session
            session_alerts = [alert for alert in self.alert_history if alert.session_id == session_id]
            
            # Statistiques des alertes
            alert_stats = {}
            for alert in session_alerts:
                alert_type = alert.alert_type.value
                if alert_type not in alert_stats:
                    alert_stats[alert_type] = {"count": 0, "severity_counts": {}}
                
                alert_stats[alert_type]["count"] += 1
                severity = alert.severity.value
                if severity not in alert_stats[alert_type]["severity_counts"]:
                    alert_stats[alert_type]["severity_counts"][severity] = 0
                alert_stats[alert_type]["severity_counts"][severity] += 1
            
            return {
                "session_id": session_id,
                "total_alerts": len(session_alerts),
                "alert_statistics": alert_stats,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {"error": str(e)}
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'une session"""
        return self.active_sessions.get(session_id)
    
    def get_recent_alerts(self, session_id: str, limit: int = 50) -> List[SurveillanceAlert]:
        """Récupère les alertes récentes pour une session"""
        session_alerts = [alert for alert in self.alert_history if alert.session_id == session_id]
        return sorted(session_alerts, key=lambda x: x.timestamp, reverse=True)[:limit]

# Instance globale du service
multimodal_surveillance_service = MultimodalSurveillanceService()
