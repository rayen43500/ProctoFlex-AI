"""
Module de surveillance IA temps réel
ProctoFlex AI - Université de Monastir - ESPRIM
"""

try:
    import cv2
    import numpy as np
    import mediapipe as mp
    AI_AVAILABLE = True
except Exception as e:
    print(f"Warning: AI dependencies not available: {e}")
    AI_AVAILABLE = False
    # Créer des objets factices pour éviter les erreurs
    cv2 = None
    np = None
    mp = None
from typing import Dict, List, Tuple, Optional, Any, Callable
import logging
import asyncio
import json
import time
from dataclasses import dataclass, asdict
from enum import Enum
import base64
from PIL import Image
import io
import threading
from collections import deque
import statistics

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(Enum):
    FACE_NOT_VISIBLE = "face_not_visible"
    MULTIPLE_FACES = "multiple_faces"
    GAZE_AWAY = "gaze_away"
    SUSPICIOUS_OBJECT = "suspicious_object"
    VOICE_DETECTED = "voice_detected"
    UNAUTHORIZED_APP = "unauthorized_app"
    COPY_PASTE_ACTIVITY = "copy_paste_activity"
    WINDOW_SWITCH = "window_switch"
    SCREEN_SHARE = "screen_share"
    NOISE_DETECTED = "noise_detected"

@dataclass
class SurveillanceAlert:
    """Alerte de surveillance"""
    id: str
    timestamp: float
    incident_type: IncidentType
    alert_level: AlertLevel
    confidence: float
    description: str
    metadata: Dict[str, Any]
    student_id: str
    exam_id: str
    session_id: str
    processed: bool = False

@dataclass
class GazeAnalysis:
    """Analyse du regard"""
    direction: str
    confidence: float
    is_looking_away: bool
    away_duration: float
    eye_landmarks: List[Tuple[int, int]]

@dataclass
class FaceAnalysis:
    """Analyse faciale"""
    is_visible: bool
    confidence: float
    face_count: int
    face_quality: float
    landmarks: List[Tuple[int, int]]
    bounding_box: Tuple[int, int, int, int]

@dataclass
class AudioAnalysis:
    """Analyse audio"""
    has_voice: bool
    voice_confidence: float
    noise_level: float
    is_speaking: bool
    speech_duration: float
    frequency_analysis: Dict[str, float]

@dataclass
class ScreenAnalysis:
    """Analyse d'écran"""
    active_window: str
    unauthorized_apps: List[str]
    copy_paste_count: int
    window_switches: int
    screen_share_detected: bool
    suspicious_activity: bool

@dataclass
class SurveillanceMetrics:
    """Métriques de surveillance"""
    total_alerts: int
    alerts_by_type: Dict[str, int]
    alerts_by_level: Dict[str, int]
    average_confidence: float
    processing_time: float
    frame_rate: float
    system_load: float

class RealTimeAIMonitoringService:
    """Service de surveillance IA temps réel"""
    
    def __init__(self):
        if not AI_AVAILABLE:
            logger.warning("AI dependencies not available, using mock implementation")
            self.face_detection = None
            self.face_mesh = None
            self.mp_face_detection = None
            self.mp_face_mesh = None
            self.mp_drawing = None
        else:
            # Initialisation MediaPipe
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_face_mesh = mp.solutions.face_mesh
            self.mp_drawing = mp.solutions.drawing_utils
            
            # Modèles
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=0.5
            )
            
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        
        # Configuration
        self.config = {
            'gaze_away_threshold': 0.3,
            'face_visibility_threshold': 0.7,
            'voice_detection_threshold': 0.5,
            'noise_threshold': 0.3,
            'processing_fps': 10,
            'alert_cooldown': 5.0,  # secondes
            'max_alerts_per_minute': 20
        }
        
        # État de surveillance
        self.is_monitoring = False
        self.current_session = None
        self.alerts_history = deque(maxlen=1000)
        self.alert_cooldowns = {}
        self.metrics = SurveillanceMetrics(
            total_alerts=0,
            alerts_by_type={},
            alerts_by_level={},
            average_confidence=0.0,
            processing_time=0.0,
            frame_rate=0.0,
            system_load=0.0
        )
        
        # Callbacks
        self.alert_callbacks: List[Callable[[SurveillanceAlert], None]] = []
        
        logger.info("Service de surveillance IA temps réel initialisé")
    
    async def start_monitoring(
        self, 
        student_id: str, 
        exam_id: str, 
        session_id: str,
        video_stream_url: Optional[str] = None,
        audio_stream_url: Optional[str] = None
    ) -> bool:
        """
        Démarre la surveillance temps réel
        
        Args:
            student_id: ID de l'étudiant
            exam_id: ID de l'examen
            session_id: ID de la session
            video_stream_url: URL du stream vidéo (optionnel)
            audio_stream_url: URL du stream audio (optionnel)
        """
        try:
            if self.is_monitoring:
                logger.warning("La surveillance est déjà active")
                return False
            
            logger.info(f"🎯 Démarrage de la surveillance pour l'étudiant {student_id}")
            
            self.current_session = {
                'student_id': student_id,
                'exam_id': exam_id,
                'session_id': session_id,
                'start_time': time.time(),
                'video_stream_url': video_stream_url,
                'audio_stream_url': audio_stream_url
            }
            
            self.is_monitoring = True
            
            # Démarrer les tâches de surveillance
            asyncio.create_task(self._video_monitoring_loop())
            asyncio.create_task(self._audio_monitoring_loop())
            asyncio.create_task(self._screen_monitoring_loop())
            asyncio.create_task(self._metrics_update_loop())
            
            logger.info("✅ Surveillance IA démarrée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage de la surveillance: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Arrête la surveillance"""
        try:
            if not self.is_monitoring:
                return True
            
            logger.info("🛑 Arrêt de la surveillance IA")
            
            self.is_monitoring = False
            self.current_session = None
            
            # Nettoyer les ressources
            self.face_detection.close()
            self.face_mesh.close()
            
            logger.info("✅ Surveillance IA arrêtée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt de la surveillance: {e}")
            return False
    
    async def process_video_frame(self, frame_data: str) -> List[SurveillanceAlert]:
        """
        Traite une frame vidéo et génère des alertes
        
        Args:
            frame_data: Frame vidéo en base64
            
        Returns:
            Liste des alertes générées
        """
        start_time = time.time()
        alerts = []
        
        try:
            # Décoder l'image
            image = self._decode_base64_image(frame_data)
            if image is None:
                return alerts
            
            # Analyser le visage
            face_analysis = await self._analyze_face(image)
            
            # Analyser le regard
            gaze_analysis = await self._analyze_gaze(image)
            
            # Générer des alertes basées sur l'analyse
            alerts.extend(self._generate_face_alerts(face_analysis))
            alerts.extend(self._generate_gaze_alerts(gaze_analysis))
            
            # Mettre à jour les métriques
            processing_time = time.time() - start_time
            self._update_processing_metrics(processing_time)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement de la frame: {e}")
        
        return alerts
    
    async def process_audio_chunk(self, audio_data: str) -> List[SurveillanceAlert]:
        """
        Traite un chunk audio et génère des alertes
        
        Args:
            audio_data: Données audio en base64
            
        Returns:
            Liste des alertes générées
        """
        alerts = []
        
        try:
            # Décoder l'audio
            audio_array = self._decode_base64_audio(audio_data)
            if audio_array is None:
                return alerts
            
            # Analyser l'audio
            audio_analysis = await self._analyze_audio(audio_array)
            
            # Générer des alertes
            alerts.extend(self._generate_audio_alerts(audio_analysis))
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement audio: {e}")
        
        return alerts
    
    async def process_screen_data(self, screen_data: Dict[str, Any]) -> List[SurveillanceAlert]:
        """
        Traite les données d'écran et génère des alertes
        
        Args:
            screen_data: Données d'écran (fenêtres actives, apps, etc.)
            
        Returns:
            Liste des alertes générées
        """
        alerts = []
        
        try:
            # Analyser l'écran
            screen_analysis = await self._analyze_screen(screen_data)
            
            # Générer des alertes
            alerts.extend(self._generate_screen_alerts(screen_analysis))
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement d'écran: {e}")
        
        return alerts
    
    async def _video_monitoring_loop(self):
        """Boucle de surveillance vidéo"""
        while self.is_monitoring:
            try:
                # En production, récupérer les frames depuis le stream
                # Pour l'instant, simulation
                await asyncio.sleep(1.0 / self.config['processing_fps'])
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle vidéo: {e}")
                await asyncio.sleep(1)
    
    async def _audio_monitoring_loop(self):
        """Boucle de surveillance audio"""
        while self.is_monitoring:
            try:
                # En production, traiter les chunks audio
                await asyncio.sleep(0.1)  # 10 FPS pour l'audio
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle audio: {e}")
                await asyncio.sleep(1)
    
    async def _screen_monitoring_loop(self):
        """Boucle de surveillance d'écran"""
        while self.is_monitoring:
            try:
                # En production, surveiller les changements d'écran
                await asyncio.sleep(0.5)  # 2 FPS pour l'écran
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle écran: {e}")
                await asyncio.sleep(1)
    
    async def _metrics_update_loop(self):
        """Boucle de mise à jour des métriques"""
        while self.is_monitoring:
            try:
                self._update_metrics()
                await asyncio.sleep(5)  # Mise à jour toutes les 5 secondes
                
            except Exception as e:
                logger.error(f"❌ Erreur dans la boucle métriques: {e}")
                await asyncio.sleep(5)
    
    async def _analyze_face(self, image) -> FaceAnalysis:
        """Analyse faciale avancée"""
        try:
            # Convertir BGR vers RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            
            # Détection des visages
            face_results = self.face_detection.process(rgb_image)
            mesh_results = self.face_mesh.process(rgb_image)
            
            is_visible = False
            confidence = 0.0
            face_count = 0
            face_quality = 0.0
            landmarks = []
            bounding_box = (0, 0, 0, 0)
            
            if face_results.detections:
                face_count = len(face_results.detections)
                detection = face_results.detections[0]
                confidence = detection.score[0]
                
                if confidence >= self.config['face_visibility_threshold']:
                    is_visible = True
                    
                    # Récupérer la bounding box
                    bbox = detection.location_data.relative_bounding_box
                    x = int(bbox.xmin * width)
                    y = int(bbox.ymin * height)
                    w = int(bbox.width * width)
                    h = int(bbox.height * height)
                    bounding_box = (x, y, w, h)
                    
                    # Calculer la qualité
                    face_roi = image[y:y+h, x:x+w]
                    face_quality = self._calculate_face_quality(face_roi)
                    
                    # Extraire les landmarks
                    if mesh_results.multi_face_landmarks:
                        landmarks = self._extract_landmarks(
                            mesh_results.multi_face_landmarks[0], width, height
                        )
            
            return FaceAnalysis(
                is_visible=is_visible,
                confidence=confidence,
                face_count=face_count,
                face_quality=face_quality,
                landmarks=landmarks,
                bounding_box=bounding_box
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse faciale: {e}")
            return FaceAnalysis(
                is_visible=False,
                confidence=0.0,
                face_count=0,
                face_quality=0.0,
                landmarks=[],
                bounding_box=(0, 0, 0, 0)
            )
    
    async def _analyze_gaze(self, image) -> GazeAnalysis:
        """Analyse du regard"""
        try:
            # Convertir BGR vers RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            
            # Obtenir les landmarks
            mesh_results = self.face_mesh.process(rgb_image)
            
            if not mesh_results.multi_face_landmarks:
                return GazeAnalysis(
                    direction="unknown",
                    confidence=0.0,
                    is_looking_away=True,
                    away_duration=0.0,
                    eye_landmarks=[]
                )
            
            landmarks = mesh_results.multi_face_landmarks[0]
            
            # Analyser la direction du regard
            direction, confidence, is_looking_away = self._calculate_gaze_direction(
                landmarks, width, height
            )
            
            # Calculer la durée d'absence
            away_duration = self._calculate_away_duration(is_looking_away)
            
            # Extraire les landmarks des yeux
            eye_landmarks = self._extract_eye_landmarks(landmarks, width, height)
            
            return GazeAnalysis(
                direction=direction,
                confidence=confidence,
                is_looking_away=is_looking_away,
                away_duration=away_duration,
                eye_landmarks=eye_landmarks
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse du regard: {e}")
            return GazeAnalysis(
                direction="unknown",
                confidence=0.0,
                is_looking_away=True,
                away_duration=0.0,
                eye_landmarks=[]
            )
    
    async def _analyze_audio(self, audio_array) -> AudioAnalysis:
        """Analyse audio"""
        try:
            # Détection de voix (simulation)
            has_voice = self._detect_voice(audio_array)
            voice_confidence = 0.8 if has_voice else 0.2
            
            # Analyse du bruit
            noise_level = self._calculate_noise_level(audio_array)
            
            # Détection de parole
            is_speaking = has_voice and voice_confidence > self.config['voice_detection_threshold']
            
            # Durée de parole (simulation)
            speech_duration = 1.0 if is_speaking else 0.0
            
            # Analyse fréquentielle
            frequency_analysis = self._analyze_frequencies(audio_array)
            
            return AudioAnalysis(
                has_voice=has_voice,
                voice_confidence=voice_confidence,
                noise_level=noise_level,
                is_speaking=is_speaking,
                speech_duration=speech_duration,
                frequency_analysis=frequency_analysis
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse audio: {e}")
            return AudioAnalysis(
                has_voice=False,
                voice_confidence=0.0,
                noise_level=0.0,
                is_speaking=False,
                speech_duration=0.0,
                frequency_analysis={}
            )
    
    async def _analyze_screen(self, screen_data: Dict[str, Any]) -> ScreenAnalysis:
        """Analyse d'écran"""
        try:
            active_window = screen_data.get('active_window', '')
            unauthorized_apps = screen_data.get('unauthorized_apps', [])
            copy_paste_count = screen_data.get('copy_paste_count', 0)
            window_switches = screen_data.get('window_switches', 0)
            screen_share_detected = screen_data.get('screen_share_detected', False)
            
            # Détecter les activités suspectes
            suspicious_activity = (
                len(unauthorized_apps) > 0 or
                copy_paste_count > 10 or
                window_switches > 20 or
                screen_share_detected
            )
            
            return ScreenAnalysis(
                active_window=active_window,
                unauthorized_apps=unauthorized_apps,
                copy_paste_count=copy_paste_count,
                window_switches=window_switches,
                screen_share_detected=screen_share_detected,
                suspicious_activity=suspicious_activity
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse d'écran: {e}")
            return ScreenAnalysis(
                active_window="",
                unauthorized_apps=[],
                copy_paste_count=0,
                window_switches=0,
                screen_share_detected=False,
                suspicious_activity=False
            )
    
    def _generate_face_alerts(self, face_analysis: FaceAnalysis) -> List[SurveillanceAlert]:
        """Génère des alertes basées sur l'analyse faciale"""
        alerts = []
        
        if not face_analysis.is_visible:
            alert = self._create_alert(
                IncidentType.FACE_NOT_VISIBLE,
                AlertLevel.HIGH,
                face_analysis.confidence,
                "Visage non visible",
                {"face_quality": face_analysis.face_quality}
            )
            alerts.append(alert)
        
        if face_analysis.face_count > 1:
            alert = self._create_alert(
                IncidentType.MULTIPLE_FACES,
                AlertLevel.CRITICAL,
                0.9,
                f"Plusieurs visages détectés ({face_analysis.face_count})",
                {"face_count": face_analysis.face_count}
            )
            alerts.append(alert)
        
        return alerts
    
    def _generate_gaze_alerts(self, gaze_analysis: GazeAnalysis) -> List[SurveillanceAlert]:
        """Génère des alertes basées sur l'analyse du regard"""
        alerts = []
        
        if gaze_analysis.is_looking_away and gaze_analysis.away_duration > 5.0:
            alert = self._create_alert(
                IncidentType.GAZE_AWAY,
                AlertLevel.MEDIUM,
                gaze_analysis.confidence,
                f"Regard détourné pendant {gaze_analysis.away_duration:.1f}s",
                {
                    "direction": gaze_analysis.direction,
                    "away_duration": gaze_analysis.away_duration
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _generate_audio_alerts(self, audio_analysis: AudioAnalysis) -> List[SurveillanceAlert]:
        """Génère des alertes basées sur l'analyse audio"""
        alerts = []
        
        if audio_analysis.is_speaking:
            alert = self._create_alert(
                IncidentType.VOICE_DETECTED,
                AlertLevel.HIGH,
                audio_analysis.voice_confidence,
                "Voix détectée pendant l'examen",
                {
                    "voice_confidence": audio_analysis.voice_confidence,
                    "speech_duration": audio_analysis.speech_duration
                }
            )
            alerts.append(alert)
        
        if audio_analysis.noise_level > self.config['noise_threshold']:
            alert = self._create_alert(
                IncidentType.NOISE_DETECTED,
                AlertLevel.LOW,
                audio_analysis.noise_level,
                "Bruit détecté",
                {"noise_level": audio_analysis.noise_level}
            )
            alerts.append(alert)
        
        return alerts
    
    def _generate_screen_alerts(self, screen_analysis: ScreenAnalysis) -> List[SurveillanceAlert]:
        """Génère des alertes basées sur l'analyse d'écran"""
        alerts = []
        
        if screen_analysis.unauthorized_apps:
            alert = self._create_alert(
                IncidentType.UNAUTHORIZED_APP,
                AlertLevel.CRITICAL,
                1.0,
                f"Applications non autorisées: {', '.join(screen_analysis.unauthorized_apps)}",
                {"unauthorized_apps": screen_analysis.unauthorized_apps}
            )
            alerts.append(alert)
        
        if screen_analysis.copy_paste_count > 10:
            alert = self._create_alert(
                IncidentType.COPY_PASTE_ACTIVITY,
                AlertLevel.MEDIUM,
                0.8,
                f"Activité copier-coller excessive: {screen_analysis.copy_paste_count}",
                {"copy_paste_count": screen_analysis.copy_paste_count}
            )
            alerts.append(alert)
        
        if screen_analysis.window_switches > 20:
            alert = self._create_alert(
                IncidentType.WINDOW_SWITCH,
                AlertLevel.MEDIUM,
                0.7,
                f"Changements de fenêtre excessifs: {screen_analysis.window_switches}",
                {"window_switches": screen_analysis.window_switches}
            )
            alerts.append(alert)
        
        if screen_analysis.screen_share_detected:
            alert = self._create_alert(
                IncidentType.SCREEN_SHARE,
                AlertLevel.CRITICAL,
                1.0,
                "Partage d'écran détecté",
                {}
            )
            alerts.append(alert)
        
        return alerts
    
    def _create_alert(
        self,
        incident_type: IncidentType,
        alert_level: AlertLevel,
        confidence: float,
        description: str,
        metadata: Dict[str, Any]
    ) -> SurveillanceAlert:
        """Crée une alerte de surveillance"""
        
        alert_id = f"alert_{int(time.time() * 1000)}_{incident_type.value}"
        
        # Vérifier le cooldown
        cooldown_key = f"{incident_type.value}_{self.current_session['student_id']}"
        if cooldown_key in self.alert_cooldowns:
            if time.time() - self.alert_cooldowns[cooldown_key] < self.config['alert_cooldown']:
                return None  # Alerte en cooldown
        
        alert = SurveillanceAlert(
            id=alert_id,
            timestamp=time.time(),
            incident_type=incident_type,
            alert_level=alert_level,
            confidence=confidence,
            description=description,
            metadata=metadata,
            student_id=self.current_session['student_id'],
            exam_id=self.current_session['exam_id'],
            session_id=self.current_session['session_id']
        )
        
        # Mettre à jour le cooldown
        self.alert_cooldowns[cooldown_key] = time.time()
        
        # Ajouter à l'historique
        self.alerts_history.append(alert)
        
        # Mettre à jour les métriques
        self._update_alert_metrics(alert)
        
        # Notifier les callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"❌ Erreur dans le callback d'alerte: {e}")
        
        return alert
    
    def _calculate_face_quality(self, face_roi) -> float:
        """Calcule la qualité d'un visage"""
        try:
            if face_roi.size == 0:
                return 0.0
            
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Netteté
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness = min(1.0, laplacian_var / 1000.0)
            
            # Luminosité
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            
            # Contraste
            contrast = np.std(gray) / 255.0
            contrast_score = min(1.0, contrast * 4)
            
            return (sharpness * 0.4 + brightness_score * 0.3 + contrast_score * 0.3)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul de la qualité: {e}")
            return 0.0
    
    def _calculate_gaze_direction(
        self, 
        landmarks, 
        width: int, 
        height: int
    ) -> Tuple[str, float, bool]:
        """Calcule la direction du regard"""
        try:
            # Points des yeux (MediaPipe face mesh)
            LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
            RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
            
            # Calculer les centres des yeux
            left_eye_center = self._calculate_eye_center(landmarks, LEFT_EYE_INDICES, width, height)
            right_eye_center = self._calculate_eye_center(landmarks, RIGHT_EYE_INDICES, width, height)
            
            if not left_eye_center or not right_eye_center:
                return "unknown", 0.0, True
            
            # Centre des deux yeux
            eye_center_x = (left_eye_center[0] + right_eye_center[0]) / 2
            eye_center_y = (left_eye_center[1] + right_eye_center[1]) / 2
            
            # Déterminer la direction
            if eye_center_x < width * 0.3:
                direction = "left"
            elif eye_center_x > width * 0.7:
                direction = "right"
            elif eye_center_y < height * 0.3:
                direction = "up"
            elif eye_center_y > height * 0.7:
                direction = "down"
            else:
                direction = "center"
            
            # Calculer la confiance
            center_x = width / 2
            center_y = height / 2
            distance_from_center = np.sqrt(
                (eye_center_x - center_x) ** 2 + (eye_center_y - center_y) ** 2
            )
            max_distance = np.sqrt(center_x ** 2 + center_y ** 2)
            confidence = 1.0 - (distance_from_center / max_distance)
            
            # Déterminer si le regard est détourné
            is_looking_away = distance_from_center > (width * self.config['gaze_away_threshold'])
            
            return direction, confidence, is_looking_away
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul du regard: {e}")
            return "unknown", 0.0, True
    
    def _calculate_eye_center(
        self, 
        landmarks, 
        eye_indices: List[int], 
        width: int, 
        height: int
    ) -> Optional[Tuple[int, int]]:
        """Calcule le centre d'un œil"""
        try:
            points = []
            for idx in eye_indices:
                if idx < len(landmarks.landmark):
                    landmark = landmarks.landmark[idx]
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    points.append((x, y))
            
            if points:
                center_x = sum(p[0] for p in points) // len(points)
                center_y = sum(p[1] for p in points) // len(points)
                return (center_x, center_y)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul du centre de l'œil: {e}")
            return None
    
    def _calculate_away_duration(self, is_looking_away: bool) -> float:
        """Calcule la durée d'absence du regard"""
        # En production, maintenir un historique des états
        return 0.0 if not is_looking_away else 1.0
    
    def _extract_eye_landmarks(
        self, 
        landmarks, 
        width: int, 
        height: int
    ) -> List[Tuple[int, int]]:
        """Extrait les landmarks des yeux"""
        try:
            eye_indices = list(range(33, 48)) + list(range(362, 398))  # Indices des yeux
            points = []
            
            for idx in eye_indices:
                if idx < len(landmarks.landmark):
                    landmark = landmarks.landmark[idx]
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    points.append((x, y))
            
            return points
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction des landmarks: {e}")
            return []
    
    def _detect_voice(self, audio_array) -> bool:
        """Détecte la présence de voix"""
        try:
            # En production, utiliser des algorithmes de détection de voix
            # Pour l'instant, simulation basée sur l'amplitude
            rms = np.sqrt(np.mean(audio_array ** 2))
            return rms > 0.01  # Seuil arbitraire
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la détection de voix: {e}")
            return False
    
    def _calculate_noise_level(self, audio_array) -> float:
        """Calcule le niveau de bruit"""
        try:
            # Calculer le RMS (Root Mean Square)
            rms = np.sqrt(np.mean(audio_array ** 2))
            return min(1.0, rms * 10)  # Normaliser
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul du bruit: {e}")
            return 0.0
    
    def _analyze_frequencies(self, audio_array) -> Dict[str, float]:
        """Analyse les fréquences audio"""
        try:
            # En production, utiliser FFT
            # Pour l'instant, simulation
            return {
                "low_freq": 0.3,
                "mid_freq": 0.5,
                "high_freq": 0.2
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse fréquentielle: {e}")
            return {}
    
    def _extract_landmarks(
        self, 
        landmarks, 
        width: int, 
        height: int
    ) -> List[Tuple[int, int]]:
        """Extrait tous les landmarks faciaux"""
        try:
            points = []
            for landmark in landmarks.landmark:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                points.append((x, y))
            return points
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction des landmarks: {e}")
            return []
    
    def _decode_base64_image(self, image_data: str):
        """Décode une image base64"""
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return np.array(image)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du décodage de l'image: {e}")
            return None
    
    def _decode_base64_audio(self, audio_data: str):
        """Décode des données audio base64"""
        try:
            if ',' in audio_data:
                audio_data = audio_data.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_data)
            # En production, décoder selon le format audio
            # Pour l'instant, simulation
            return np.random.random(1024)  # Simulation
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du décodage audio: {e}")
            return None
    
    def _update_processing_metrics(self, processing_time: float):
        """Met à jour les métriques de traitement"""
        self.metrics.processing_time = processing_time
        self.metrics.frame_rate = 1.0 / processing_time if processing_time > 0 else 0.0
    
    def _update_alert_metrics(self, alert: SurveillanceAlert):
        """Met à jour les métriques d'alertes"""
        self.metrics.total_alerts += 1
        
        # Alertes par type
        incident_type = alert.incident_type.value
        self.metrics.alerts_by_type[incident_type] = self.metrics.alerts_by_type.get(incident_type, 0) + 1
        
        # Alertes par niveau
        alert_level = alert.alert_level.value
        self.metrics.alerts_by_level[alert_level] = self.metrics.alerts_by_level.get(alert_level, 0) + 1
        
        # Confiance moyenne
        confidences = [a.confidence for a in self.alerts_history]
        self.metrics.average_confidence = statistics.mean(confidences) if confidences else 0.0
    
    def _update_metrics(self):
        """Met à jour toutes les métriques"""
        # En production, calculer la charge système
        self.metrics.system_load = 0.5  # Simulation
    
    def add_alert_callback(self, callback: Callable[[SurveillanceAlert], None]):
        """Ajoute un callback pour les alertes"""
        self.alert_callbacks.append(callback)
    
    def get_metrics(self) -> SurveillanceMetrics:
        """Obtient les métriques actuelles"""
        return self.metrics
    
    def get_recent_alerts(self, limit: int = 50) -> List[SurveillanceAlert]:
        """Obtient les alertes récentes"""
        return list(self.alerts_history)[-limit:]
    
    def get_alerts_by_type(self, incident_type: IncidentType) -> List[SurveillanceAlert]:
        """Obtient les alertes par type"""
        return [alert for alert in self.alerts_history if alert.incident_type == incident_type]
    
    def get_alerts_by_level(self, alert_level: AlertLevel) -> List[SurveillanceAlert]:
        """Obtient les alertes par niveau"""
        return [alert for alert in self.alerts_history if alert.alert_level == alert_level]
    
    def cleanup(self):
        """Nettoie les ressources"""
        try:
            if self.is_monitoring:
                asyncio.create_task(self.stop_monitoring())
            
            self.face_detection.close()
            self.face_mesh.close()
            self.alerts_history.clear()
            self.alert_cooldowns.clear()
            
            logger.info("✅ Service de surveillance IA nettoyé")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage: {e}")

# Instance globale du service
real_time_ai_monitoring_service = RealTimeAIMonitoringService()
