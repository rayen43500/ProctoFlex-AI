"""
Module de vérification d'identité par reconnaissance faciale
ProctoFlex AI - Université de Monastir
"""

import cv2
import numpy as np
import face_recognition
from typing import Dict, List, Tuple, Optional
import logging
from PIL import Image
import io
import base64
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class VerificationResult(Enum):
    VERIFIED = "verified"
    REJECTED = "rejected"
    UNCERTAIN = "uncertain"

@dataclass
class IdentityVerification:
    """Résultat de la vérification d'identité"""
    result: VerificationResult
    confidence: float
    distance: float
    threshold: float
    face_detected: bool
    multiple_faces: bool
    quality_score: float
    reason: str
    processing_time: float

class IdentityVerificationService:
    """Service de vérification d'identité par reconnaissance faciale"""
    
    def __init__(self):
        self.confidence_threshold = 0.8
        self.distance_threshold = 0.6
        self.min_face_size = 100  # pixels
        self.max_processing_time = 5.0  # secondes
        
    def verify_identity(
        self, 
        current_image: str, 
        reference_image: str,
        student_id: Optional[str] = None
    ) -> IdentityVerification:
        """
        Vérifie l'identité d'un étudiant en comparant deux images
        
        Args:
            current_image: Image actuelle (base64)
            reference_image: Image de référence (base64)
            student_id: ID de l'étudiant (optionnel)
            
        Returns:
            IdentityVerification: Résultat de la vérification
        """
        import time
        start_time = time.time()
        
        try:
            logger.info(f"Début de la vérification d'identité pour l'étudiant {student_id}")
            
            # Décoder les images
            current_img = self._decode_base64_image(current_image)
            reference_img = self._decode_base64_image(reference_image)
            
            if current_img is None or reference_img is None:
                return IdentityVerification(
                    result=VerificationResult.REJECTED,
                    confidence=0.0,
                    distance=1.0,
                    threshold=self.distance_threshold,
                    face_detected=False,
                    multiple_faces=False,
                    quality_score=0.0,
                    reason="Impossible de décoder les images",
                    processing_time=time.time() - start_time
                )
            
            # Détecter les visages dans l'image actuelle
            current_faces = self._detect_faces(current_img)
            if not current_faces:
                return IdentityVerification(
                    result=VerificationResult.REJECTED,
                    confidence=0.0,
                    distance=1.0,
                    threshold=self.distance_threshold,
                    face_detected=False,
                    multiple_faces=False,
                    quality_score=0.0,
                    reason="Aucun visage détecté dans l'image actuelle",
                    processing_time=time.time() - start_time
                )
            
            # Vérifier s'il y a plusieurs visages
            multiple_faces = len(current_faces) > 1
            if multiple_faces:
                logger.warning(f"Plusieurs visages détectés ({len(current_faces)})")
            
            # Détecter les visages dans l'image de référence
            reference_faces = self._detect_faces(reference_img)
            if not reference_faces:
                return IdentityVerification(
                    result=VerificationResult.REJECTED,
                    confidence=0.0,
                    distance=1.0,
                    threshold=self.distance_threshold,
                    face_detected=True,
                    multiple_faces=multiple_faces,
                    quality_score=0.0,
                    reason="Aucun visage détecté dans l'image de référence",
                    processing_time=time.time() - start_time
                )
            
            # Utiliser le premier visage détecté
            current_face = current_faces[0]
            reference_face = reference_faces[0]
            
            # Calculer la qualité des visages
            current_quality = self._calculate_face_quality(current_img, current_face)
            reference_quality = self._calculate_face_quality(reference_img, reference_face)
            
            # Comparer les visages
            distance = face_recognition.face_distance([reference_face], current_face)[0]
            confidence = max(0.0, 1.0 - distance)
            
            # Déterminer le résultat
            if distance <= self.distance_threshold and confidence >= self.confidence_threshold:
                result = VerificationResult.VERIFIED
                reason = "Identité vérifiée avec succès"
            elif distance <= self.distance_threshold * 1.2:
                result = VerificationResult.UNCERTAIN
                reason = "Correspondance incertaine - vérification manuelle recommandée"
            else:
                result = VerificationResult.REJECTED
                reason = "Les visages ne correspondent pas"
            
            processing_time = time.time() - start_time
            
            logger.info(f"Vérification terminée: {result.value}, confiance: {confidence:.3f}, distance: {distance:.3f}")
            
            return IdentityVerification(
                result=result,
                confidence=confidence,
                distance=distance,
                threshold=self.distance_threshold,
                face_detected=True,
                multiple_faces=multiple_faces,
                quality_score=(current_quality + reference_quality) / 2,
                reason=reason,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'identité: {e}")
            return IdentityVerification(
                result=VerificationResult.REJECTED,
                confidence=0.0,
                distance=1.0,
                threshold=self.distance_threshold,
                face_detected=False,
                multiple_faces=False,
                quality_score=0.0,
                reason=f"Erreur technique: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _decode_base64_image(self, image_data: str) -> Optional[np.ndarray]:
        """Décode une image base64 en array numpy"""
        try:
            # Supprimer le préfixe data:image/...;base64, si présent
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # Décoder l'image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convertir en RGB si nécessaire
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convertir en array numpy
            return np.array(image)
            
        except Exception as e:
            logger.error(f"Erreur lors du décodage de l'image: {e}")
            return None
    
    def _detect_faces(self, image: np.ndarray) -> List[np.ndarray]:
        """Détecte les visages dans une image et retourne les encodages"""
        try:
            # Détecter les emplacements des visages
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return []
            
            # Encoder les visages
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            return face_encodings
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection des visages: {e}")
            return []
    
    def _calculate_face_quality(self, image: np.ndarray, face_encoding: np.ndarray) -> float:
        """Calcule la qualité d'un visage détecté"""
        try:
            # Trouver l'emplacement du visage
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return 0.0
            
            # Utiliser le premier visage trouvé
            face_location = face_locations[0]
            top, right, bottom, left = face_location
            
            # Calculer la taille du visage
            face_width = right - left
            face_height = bottom - top
            face_size = face_width * face_height
            
            # Score de qualité basé sur la taille
            size_score = min(1.0, face_size / (self.min_face_size ** 2))
            
            # Score de qualité basé sur la netteté (simulation)
            # En production, utiliser des algorithmes de détection de flou
            sharpness_score = 0.8  # Simulation
            
            # Score de qualité basé sur l'éclairage (simulation)
            # En production, analyser l'histogramme de l'image
            lighting_score = 0.7  # Simulation
            
            # Score global
            quality_score = (size_score * 0.4 + sharpness_score * 0.3 + lighting_score * 0.3)
            
            return min(1.0, quality_score)
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la qualité du visage: {e}")
            return 0.0
    
    def validate_image_quality(self, image_data: str) -> Dict[str, any]:
        """Valide la qualité d'une image pour la vérification d'identité"""
        try:
            image = self._decode_base64_image(image_data)
            if image is None:
                return {
                    "valid": False,
                    "reason": "Impossible de décoder l'image",
                    "quality_score": 0.0
                }
            
            # Détecter les visages
            faces = self._detect_faces(image)
            
            if not faces:
                return {
                    "valid": False,
                    "reason": "Aucun visage détecté",
                    "quality_score": 0.0
                }
            
            if len(faces) > 1:
                return {
                    "valid": False,
                    "reason": "Plusieurs visages détectés",
                    "quality_score": 0.0
                }
            
            # Calculer la qualité
            quality = self._calculate_face_quality(image, faces[0])
            
            return {
                "valid": quality >= 0.5,
                "reason": "Image valide" if quality >= 0.5 else "Qualité d'image insuffisante",
                "quality_score": quality
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de l'image: {e}")
            return {
                "valid": False,
                "reason": f"Erreur technique: {str(e)}",
                "quality_score": 0.0
            }

# Instance globale du service
identity_verification_service = IdentityVerificationService()
