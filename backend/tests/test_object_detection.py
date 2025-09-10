from app.ai.object_detection import ObjectDetectionService
import base64
import numpy as np
import cv2

def create_blank_image_b64(width=320, height=240, color=(255,255,255)):
    img = np.full((height, width, 3), color, dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', img)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf).decode()

def test_object_detection_runs_without_model():
    service = ObjectDetectionService()
    # Forcer désactivation YOLO pour test rapide si modèle absent
    img_b64 = create_blank_image_b64()
    result = service.detect_suspicious_objects(img_b64)
    assert 'objects_detected' in result
    assert result['objects_detected'] >= 0
