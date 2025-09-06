"""
Module de reconnaissance faciale avancée avec OpenCV et MediaPipe
ProctoFlex AI - Université de Monastir - ESPRIM
"""

try:
    import cv2
    import numpy as np
    import mediapipe as mp
    AI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI dependencies not available: {e}")
    AI_AVAILABLE = False
    # Créer des objets factices pour éviter les erreurs
    cv2 = None
    np = None
    mp = None
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum
import time
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)

class FaceQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class GazeDirection(Enum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    AWAY = "away"

@dataclass
class FaceDetectionResult:
    """Résultat de la détection faciale"""
    faces_detected: int
    face_locations: List[Dict[str, int]]
    face_landmarks: List[List[Tuple[int, int]]]
    face_encodings: List[Any]
    quality_scores: List[float]
    gaze_directions: List[GazeDirection]
    confidence_scores: List[float]
    processing_time: float

@dataclass
class IdentityVerificationResult:
    """Résultat de la vérification d'identité"""
    verified: bool
    confidence: float
    distance: float
    threshold: float
    face_match_quality: float
    liveness_detected: bool
    spoofing_detected: bool
    reason: str
    processing_time: float

class AdvancedFaceRecognitionService:
    """Service de reconnaissance faciale avancée avec MediaPipe et OpenCV"""
    
    def __init__(self):
        if not AI_AVAILABLE:
            logger.warning("AI dependencies not available, using mock implementation")
            self.face_detection = None
            self.face_mesh = None
            self.mp_face_detection = None
            self.mp_face_mesh = None
            self.mp_drawing = None
            return
            
        # Initialisation de MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Modèles MediaPipe
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 pour visages proches, 1 pour visages éloignés
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
        self.face_quality_threshold = 0.7
        self.gaze_threshold = 0.3
        self.liveness_threshold = 0.8
        
        # Cache pour les encodages de visages
        self.face_encodings_cache = {}
        
        logger.info("Service de reconnaissance faciale avancée initialisé")
    
    def detect_faces_advanced(self, image) -> FaceDetectionResult:
        """
        Détection faciale avancée avec MediaPipe et OpenCV
        
        Args:
            image: Image en format numpy array (BGR)
            
        Returns:
            FaceDetectionResult: Résultat complet de la détection
        """
        start_time = time.time()
        
        if not AI_AVAILABLE:
            return FaceDetectionResult(
                faces_detected=0,
                face_locations=[],
                face_landmarks=[],
                face_encodings=[],
                quality_scores=[],
                gaze_directions=[],
                confidence_scores=[],
                processing_time=time.time() - start_time
            )
        
        try:
            # Convertir BGR vers RGB pour MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            
            # Détection des visages avec MediaPipe
            face_detection_results = self.face_detection.process(rgb_image)
            face_mesh_results = self.face_mesh.process(rgb_image)
            
            faces_detected = 0
            face_locations = []
            face_landmarks = []
            face_encodings = []
            quality_scores = []
            gaze_directions = []
            confidence_scores = []
            
            if face_detection_results.detections:
                faces_detected = len(face_detection_results.detections)
                
                for i, detection in enumerate(face_detection_results.detections):
                    # Récupérer la bounding box
                    bbox = detection.location_data.relative_bounding_box
                    x = int(bbox.xmin * width)
                    y = int(bbox.ymin * height)
                    w = int(bbox.width * width)
                    h = int(bbox.height * height)
                    
                    face_locations.append({
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'top': y, 'right': x + w, 'bottom': y + h, 'left': x
                    })
                    
                    # Score de confiance
                    confidence = detection.score[0]
                    confidence_scores.append(confidence)
                    
                    # Extraire le visage
                    face_roi = image[y:y+h, x:x+w]
                    
                    # Calculer la qualité du visage
                    quality = self._calculate_face_quality(face_roi)
                    quality_scores.append(quality)
                    
                    # Encoder le visage
                    face_encoding = self._encode_face(face_roi)
                    face_encodings.append(face_encoding)
                    
                    # Analyser le regard si des landmarks sont disponibles
                    if face_mesh_results.multi_face_landmarks and i < len(face_mesh_results.multi_face_landmarks):
                        landmarks = face_mesh_results.multi_face_landmarks[i]
                        face_landmarks.append(self._extract_landmarks(landmarks, width, height))
                        
                        # Analyser la direction du regard
                        gaze_direction = self._analyze_gaze_direction(landmarks, width, height)
                        gaze_directions.append(gaze_direction)
                    else:
                        face_landmarks.append([])
                        gaze_directions.append(GazeDirection.CENTER)
            
            processing_time = time.time() - start_time
            
            return FaceDetectionResult(
                faces_detected=faces_detected,
                face_locations=face_locations,
                face_landmarks=face_landmarks,
                face_encodings=face_encodings,
                quality_scores=quality_scores,
                gaze_directions=gaze_directions,
                confidence_scores=confidence_scores,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection faciale avancée: {e}")
            return FaceDetectionResult(
                faces_detected=0,
                face_locations=[],
                face_landmarks=[],
                face_encodings=[],
                quality_scores=[],
                gaze_directions=[],
                confidence_scores=[],
                processing_time=time.time() - start_time
            )
    
    def verify_identity_advanced(
        self, 
        current_image: str, 
        reference_image: str,
        student_id: Optional[str] = None
    ) -> IdentityVerificationResult:
        """
        Vérification d'identité avancée avec détection de spoofing
        
        Args:
            current_image: Image actuelle (base64)
            reference_image: Image de référence (base64)
            student_id: ID de l'étudiant
            
        Returns:
            IdentityVerificationResult: Résultat de la vérification
        """
        start_time = time.time()
        
        try:
            # Décoder les images
            current_img = self._decode_base64_image(current_image)
            reference_img = self._decode_base64_image(reference_image)
            
            if current_img is None or reference_img is None:
                return IdentityVerificationResult(
                    verified=False,
                    confidence=0.0,
                    distance=1.0,
                    threshold=0.6,
                    face_match_quality=0.0,
                    liveness_detected=False,
                    spoofing_detected=True,
                    reason="Impossible de décoder les images",
                    processing_time=time.time() - start_time
                )
            
            # Détecter les visages dans les deux images
            current_faces = self.detect_faces_advanced(current_img)
            reference_faces = self.detect_faces_advanced(reference_img)
            
            if current_faces.faces_detected == 0:
                return IdentityVerificationResult(
                    verified=False,
                    confidence=0.0,
                    distance=1.0,
                    threshold=0.6,
                    face_match_quality=0.0,
                    liveness_detected=False,
                    spoofing_detected=False,
                    reason="Aucun visage détecté dans l'image actuelle",
                    processing_time=time.time() - start_time
                )
            
            if reference_faces.faces_detected == 0:
                return IdentityVerificationResult(
                    verified=False,
                    confidence=0.0,
                    distance=1.0,
                    threshold=0.6,
                    face_match_quality=0.0,
                    liveness_detected=False,
                    spoofing_detected=False,
                    reason="Aucun visage détecté dans l'image de référence",
                    processing_time=time.time() - start_time
                )
            
            # Vérifier la qualité des visages
            current_quality = current_faces.quality_scores[0] if current_faces.quality_scores else 0
            reference_quality = reference_faces.quality_scores[0] if reference_faces.quality_scores else 0
            
            if current_quality < self.face_quality_threshold:
                return IdentityVerificationResult(
                    verified=False,
                    confidence=0.0,
                    distance=1.0,
                    threshold=0.6,
                    face_match_quality=current_quality,
                    liveness_detected=False,
                    spoofing_detected=False,
                    reason="Qualité d'image insuffisante",
                    processing_time=time.time() - start_time
                )
            
            # Détecter le spoofing (anti-fraude)
            spoofing_detected = self._detect_spoofing(current_img)
            liveness_detected = not spoofing_detected
            
            if spoofing_detected:
                return IdentityVerificationResult(
                    verified=False,
                    confidence=0.0,
                    distance=1.0,
                    threshold=0.6,
                    face_match_quality=current_quality,
                    liveness_detected=False,
                    spoofing_detected=True,
                    reason="Tentative de fraude détectée",
                    processing_time=time.time() - start_time
                )
            
            # Comparer les visages
            current_encoding = current_faces.face_encodings[0]
            reference_encoding = reference_faces.face_encodings[0]
            
            # Calculer la distance entre les encodages
            distance = np.linalg.norm(current_encoding - reference_encoding)
            confidence = max(0.0, 1.0 - distance)
            
            # Déterminer si les visages correspondent
            threshold = 0.6
            verified = distance <= threshold and confidence >= 0.8
            
            reason = "Identité vérifiée avec succès" if verified else "Les visages ne correspondent pas"
            
            processing_time = time.time() - start_time
            
            return IdentityVerificationResult(
                verified=verified,
                confidence=confidence,
                distance=distance,
                threshold=threshold,
                face_match_quality=(current_quality + reference_quality) / 2,
                liveness_detected=liveness_detected,
                spoofing_detected=spoofing_detected,
                reason=reason,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'identité avancée: {e}")
            return IdentityVerificationResult(
                verified=False,
                confidence=0.0,
                distance=1.0,
                threshold=0.6,
                face_match_quality=0.0,
                liveness_detected=False,
                spoofing_detected=False,
                reason=f"Erreur technique: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _calculate_face_quality(self, face_roi) -> float:
        """Calcule la qualité d'un visage détecté"""
        try:
            if face_roi.size == 0:
                return 0.0
            
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Calculer la netteté (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 1000.0)
            
            # Calculer la luminosité
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2  # Optimal autour de 0.5
            
            # Calculer le contraste
            contrast = np.std(gray) / 255.0
            contrast_score = min(1.0, contrast * 4)  # Normaliser
            
            # Calculer la symétrie (simulation)
            symmetry_score = 0.8  # En production, analyser la symétrie faciale
            
            # Score global pondéré
            quality_score = (
                sharpness_score * 0.4 +
                brightness_score * 0.3 +
                contrast_score * 0.2 +
                symmetry_score * 0.1
            )
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la qualité: {e}")
            return 0.0
    
    def _encode_face(self, face_roi) -> Any:
        """Encode un visage en vecteur de caractéristiques"""
        try:
            # Redimensionner le visage
            face_resized = cv2.resize(face_roi, (128, 128))
            
            # Convertir en niveaux de gris
            gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Normaliser
            normalized = gray.astype(np.float32) / 255.0
            
            # Aplatir en vecteur
            encoding = normalized.flatten()
            
            return encoding
            
        except Exception as e:
            logger.error(f"Erreur lors de l'encodage du visage: {e}")
            return np.zeros(128 * 128, dtype=np.float32)
    
    def _extract_landmarks(self, landmarks, width: int, height: int) -> List[Tuple[int, int]]:
        """Extrait les landmarks faciaux"""
        try:
            points = []
            for landmark in landmarks.landmark:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                points.append((x, y))
            return points
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des landmarks: {e}")
            return []
    
    def _analyze_gaze_direction(self, landmarks, width: int, height: int) -> GazeDirection:
        """Analyse la direction du regard"""
        try:
            # Points clés pour l'analyse du regard
            # MediaPipe face mesh indices pour les yeux
            LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
            RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
            
            # Calculer le centre des yeux
            left_eye_center = self._calculate_eye_center(landmarks, LEFT_EYE_INDICES, width, height)
            right_eye_center = self._calculate_eye_center(landmarks, RIGHT_EYE_INDICES, width, height)
            
            if left_eye_center and right_eye_center:
                # Calculer la direction du regard
                eye_center_x = (left_eye_center[0] + right_eye_center[0]) / 2
                eye_center_y = (left_eye_center[1] + right_eye_center[1]) / 2
                
                # Déterminer la direction basée sur la position relative
                if eye_center_x < width * 0.3:
                    return GazeDirection.LEFT
                elif eye_center_x > width * 0.7:
                    return GazeDirection.RIGHT
                elif eye_center_y < height * 0.3:
                    return GazeDirection.UP
                elif eye_center_y > height * 0.7:
                    return GazeDirection.DOWN
                else:
                    return GazeDirection.CENTER
            
            return GazeDirection.CENTER
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du regard: {e}")
            return GazeDirection.CENTER
    
    def _calculate_eye_center(self, landmarks, eye_indices: List[int], width: int, height: int) -> Optional[Tuple[int, int]]:
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
            logger.error(f"Erreur lors du calcul du centre de l'œil: {e}")
            return None
    
    def _detect_spoofing(self, image) -> bool:
        """Détecte les tentatives de spoofing (photos, vidéos)"""
        try:
            # Méthodes de détection de spoofing basiques
            # En production, utiliser des modèles ML avancés
            
            # 1. Vérifier la texture de la peau
            skin_texture_score = self._analyze_skin_texture(image)
            
            # 2. Vérifier la profondeur (simulation)
            depth_score = 0.8  # En production, utiliser la stéréo vision
            
            # 3. Vérifier les mouvements oculaires (simulation)
            blink_score = 0.7  # En production, analyser les clignements
            
            # Score global de spoofing
            spoofing_score = (skin_texture_score + depth_score + blink_score) / 3
            
            return spoofing_score < self.liveness_threshold
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de spoofing: {e}")
            return False
    
    def _analyze_skin_texture(self, image) -> float:
        """Analyse la texture de la peau pour détecter les faux visages"""
        try:
            # Convertir en HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Masque de peau
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Calculer la variance de la texture
            texture_variance = cv2.Laplacian(skin_mask, cv2.CV_64F).var()
            
            # Normaliser le score
            texture_score = min(1.0, texture_variance / 1000.0)
            
            return texture_score
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la texture: {e}")
            return 0.5
    
    def _decode_base64_image(self, image_data: str):
        """Décode une image base64 en array numpy"""
        try:
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return np.array(image)
            
        except Exception as e:
            logger.error(f"Erreur lors du décodage de l'image: {e}")
            return None
    
    def cleanup(self):
        """Nettoie les ressources"""
        try:
            self.face_detection.close()
            self.face_mesh.close()
            logger.info("Service de reconnaissance faciale nettoyé")
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")

# Instance globale du service
advanced_face_recognition_service = AdvancedFaceRecognitionService()
