import cv2
import numpy as np
import os
from typing import List, Tuple, Optional
from ai.yolo_face_detection import YOLOFaceDetector, detect_faces_yolo

class FaceDetector:
    """
    Face detection using YOLOv8 (Deep Learning)
    Superior accuracy compared to traditional Haar Cascade
    """
    
    def __init__(self, model_size: str = 'n'):
        """
        Initialize YOLOv8 face detector
        
        Args:
            model_size: 'n'=nano (fastest), 's'=small, 'm'=medium, 'l'=large, 'x'=xlarge (most accurate)
        """
        self.yolo_detector = YOLOFaceDetector(
            model_size=model_size,
            confidence_threshold=0.5,
            iou_threshold=0.45
        )
        
    def detect_faces(self, image_path: str) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image using YOLOv8
        Returns list of bounding boxes (x, y, width, height)
        """
        try:
            # Use YOLOv8 for detection
            faces = self.yolo_detector.detect_faces(image_path)
            
            # Convert to format expected by legacy code: [(x, y, w, h), ...]
            bounding_boxes = []
            for face in faces:
                bbox = face['bounding_box']  # (x, y, w, h)
                bounding_boxes.append(bbox)
            
            return bounding_boxes
            
        except Exception as e:
            print(f"Error detecting faces: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_face_features(self, image_path: str, face_box: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Extract facial features from a detected face region
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Extract face region using bounding box
            x, y, w, h = face_box
            face_region = img[y:y+h, x:x+w]
            
            # Resize to standard size
            face_region = cv2.resize(face_region, (160, 160))  # Standard for deep learning models
            
            return face_region
            
        except Exception as e:
            print(f"Error extracting face features: {e}")
            return None
    
    # Note: LBPH training methods removed - now using DeepFace for recognition
    # DeepFace uses pre-trained CNN models, no training required
    
    def compare_faces(self, image1_path: str, image2_path: str, threshold: float = 0.6) -> bool:
        """
        Compare two face images using DeepFace and return True if they match
        """
        try:
            from ai.deepface_recognition import DeepFaceRecognizer
            
            recognizer = DeepFaceRecognizer(model_name='Facenet')
            result = recognizer.verify_faces(image1_path, image2_path)
            
            # DeepFace returns 'verified' boolean and 'distance'
            is_match = result.get('verified', False)
            distance = result.get('distance', 1.0)
            
            print(f"🔍 Face comparison: verified={is_match}, distance={distance:.4f}")
            
            return is_match
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # Note: Model save/load removed - DeepFace uses pre-trained models

# Utility functions for the missing person system
def find_similar_faces(target_image_path: str, database_folder: str, threshold: float = 0.6) -> List[str]:
    """
    Find faces in database that match the target image
    Returns list of matching image paths
    """
    detector = FaceDetector()
    matches = []
    
    if not os.path.exists(target_image_path):
        print(f"Target image not found: {target_image_path}")
        return matches
    
    if not os.path.exists(database_folder):
        print(f"Database folder not found: {database_folder}")
        return matches
    
    # Iterate through all images in database
    for filename in os.listdir(database_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            db_image_path = os.path.join(database_folder, filename)
            
            # Compare faces
            if detector.compare_faces(target_image_path, db_image_path, threshold):
                matches.append(db_image_path)
    
    return matches

def detect_and_crop_faces(image_path: str, output_folder: str) -> List[str]:
    """
    Detect faces in an image and save cropped faces
    Returns list of cropped face image paths
    """
    detector = FaceDetector()
    cropped_faces = []
    
    # Detect faces
    faces = detector.detect_faces(image_path)
    
    # Read original image
    img = cv2.imread(image_path)
    if img is None:
        return cropped_faces
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Crop and save each face
    for i, (x, y, w, h) in enumerate(faces):
        face_region = img[y:y+h, x:x+w]
        
        # Save cropped face
        output_path = os.path.join(output_folder, f"face_{i}_{os.path.basename(image_path)}")
        cv2.imwrite(output_path, face_region)
        cropped_faces.append(output_path)
    
    return cropped_faces