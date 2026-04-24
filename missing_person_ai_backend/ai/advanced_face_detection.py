"""
Advanced Face Detection Service
Supports multiple detection engines:
- YOLOv8 (state-of-the-art, highest accuracy)
- RetinaFace (most accurate)
- MTCNN (good accuracy)
- MediaPipe (real-time)
"""

import cv2
import numpy as np
import os
from typing import List, Tuple, Dict, Optional

# Try to import advanced libraries with fallback
try:
    from retinaface import RetinaFace
    RETINAFACE_AVAILABLE = True
except ImportError:
    RETINAFACE_AVAILABLE = False
    print("⚠️ RetinaFace not available, will use MTCNN or MediaPipe")

try:
    from mtcnn import MTCNN
    MTCNN_AVAILABLE = True
except ImportError:
    MTCNN_AVAILABLE = False
    print("⚠️ MTCNN not available")

try:
    import mediapipe
    # Test if mediapipe.solutions is accessible
    _ = mediapipe.solutions.face_detection
    MEDIAPIPE_AVAILABLE = True
    mp = mediapipe
except (ImportError, AttributeError):
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe not available")

try:
    from ai.yolo_face_detection import YOLOFaceDetector
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️ YOLO not available")


class AdvancedFaceDetector:
    """Advanced face detection using multiple engines"""
    
    def __init__(self, engine: str = 'yolov8'):
        """
        Initialize face detector
        
        Args:
            engine: Detection engine ('yolov8', 'retinaface', 'mtcnn', 'mediapipe', 'opencv')
        """
        # Auto-select best available engine
        if engine == 'yolov8' and not YOLO_AVAILABLE:
            print("⚠️ YOLO not available, falling back to RetinaFace")
            engine = 'retinaface'
        
        if engine == 'retinaface' and not RETINAFACE_AVAILABLE:
            print("⚠️ RetinaFace not available, falling back to MediaPipe")
            engine = 'mediapipe'
        
        if engine == 'mtcnn' and not MTCNN_AVAILABLE:
            print("⚠️ MTCNN not available, falling back to MediaPipe")
            engine = 'mediapipe'
        
        if engine == 'mediapipe' and not MEDIAPIPE_AVAILABLE:
            print("⚠️ MediaPipe not available, falling back to OpenCV")
            engine = 'opencv'
        
        self.engine = engine
        
        # Initialize YOLO detector if available
        if YOLO_AVAILABLE:
            self.yolo_detector = YOLOFaceDetector(model_size='n', confidence_threshold=0.5)
        
        # Initialize MTCNN detector if available
        if MTCNN_AVAILABLE:
            self.mtcnn_detector = MTCNN()
        
        # Initialize MediaPipe if available
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_drawing = mp.solutions.drawing_utils
            self.mediapipe_detector = self.mp_face_detection.FaceDetection(
                min_detection_confidence=0.5
            )
        
        # Initialize OpenCV fallback
        self.opencv_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        print(f"✅ AdvancedFaceDetector initialized with engine: {engine}")
    
    def detect_faces_yolov8(self, image_path: str) -> List[Dict]:
        """
        Detect faces using YOLOv8 (state-of-the-art accuracy)
        
        Returns:
            List of dictionaries with face data
        """
        if not YOLO_AVAILABLE:
            print("❌ YOLO not available")
            return []
        
        try:
            faces = self.yolo_detector.detect_faces(image_path)
            print(f"✅ YOLOv8 detected {len(faces)} face(s)")
            return faces
            
        except Exception as e:
            print(f"❌ YOLOv8 detection error: {e}")
            return []
    
    def detect_faces_retinaface(self, image_path: str) -> List[Dict]:
        """
        Detect faces using RetinaFace (most accurate)
        
        Returns:
            List of dictionaries with face data
        """
        if not RETINAFACE_AVAILABLE:
            print("❌ RetinaFace not available")
            return []
        
        try:
            # RetinaFace expects image path or numpy array
            result = RetinaFace.detect_faces(image_path)
            
            if not isinstance(result, dict):
                return []
            
            faces = []
            img = cv2.imread(image_path)
            
            for face_id, face_info in result.items():
                facial_area = face_info['facial_area']
                confidence = face_info['score']
                landmarks = face_info.get('landmarks', {})
                
                # Extract bounding box (x, y, w, h)
                x1, y1, x2, y2 = facial_area
                x, y, w, h = x1, y1, x2 - x1, y2 - y1
                
                # Crop face
                cropped_face = img[y1:y2, x1:x2] if y2 > y1 and x2 > x1 else None
                
                faces.append({
                    'bounding_box': (x, y, w, h),
                    'confidence': float(confidence),
                    'landmarks': landmarks,
                    'cropped_face': cropped_face,
                    'engine': 'retinaface'
                })
            
            print(f"✅ RetinaFace detected {len(faces)} face(s)")
            return faces
            
        except Exception as e:
            print(f"❌ RetinaFace detection error: {e}")
            return []
    
    def detect_faces_mtcnn(self, image_path: str) -> List[Dict]:
        """
        Detect faces using MTCNN (Multi-task Cascaded Convolutional Networks)
        
        Returns:
            List of dictionaries with face data
        """
        if not MTCNN_AVAILABLE:
            print("❌ MTCNN not available")
            return []
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert BGR to RGB (MTCNN expects RGB)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            detections = self.mtcnn_detector.detect_faces(img_rgb)
            
            faces = []
            for detection in detections:
                box = detection['box']  # (x, y, w, h)
                confidence = detection['confidence']
                landmarks = detection.get('keypoints', {})
                
                # Extract bounding box
                x, y, w, h = box
                
                # Crop face (with padding)
                x1, y1 = max(0, x), max(0, y)
                x2, y2 = min(img.shape[1], x + w), min(img.shape[0], y + h)
                cropped_face = img[y1:y2, x1:x2]
                
                faces.append({
                    'bounding_box': (x, y, w, h),
                    'confidence': float(confidence),
                    'landmarks': landmarks,
                    'cropped_face': cropped_face,
                    'engine': 'mtcnn'
                })
            
            print(f"✅ MTCNN detected {len(faces)} face(s)")
            return faces
            
        except Exception as e:
            print(f"❌ MTCNN detection error: {e}")
            return []
    
    def detect_faces_mediapipe(self, image_path: str) -> List[Dict]:
        """
        Detect faces using MediaPipe (fastest, good for real-time)
        
        Returns:
            List of dictionaries with face data
        """
        if not MEDIAPIPE_AVAILABLE:
            print("❌ MediaPipe not available")
            return []
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            results = self.mediapipe_detector.process(img_rgb)
            
            faces = []
            if results.detections:
                for detection in results.detections:
                    # Extract bounding box
                    bboxC = detection.location_data.relative_bounding_box
                    h, w, c = img.shape
                    
                    x = int(bboxC.xmin * w)
                    y = int(bboxC.ymin * h)
                    bw = int(bboxC.width * w)
                    bh = int(bboxC.height * h)
                    
                    # Ensure coordinates are within image bounds
                    x = max(0, x)
                    y = max(0, y)
                    x2 = min(w, x + bw)
                    y2 = min(h, y + bh)
                    
                    # Crop face
                    cropped_face = img[y:y2, x:x2]
                    
                    # Extract confidence
                    confidence = detection.score[0] if detection.score else 0.0
                    
                    faces.append({
                        'bounding_box': (x, y, bw, bh),
                        'confidence': float(confidence),
                        'landmarks': {},
                        'cropped_face': cropped_face,
                        'engine': 'mediapipe'
                    })
            
            print(f"✅ MediaPipe detected {len(faces)} face(s)")
            return faces
            
        except Exception as e:
            print(f"❌ MediaPipe detection error: {e}")
            return []
    
    def detect_faces_opencv(self, image_path: str) -> List[Dict]:
        """
        Detect faces using OpenCV Haar Cascade (fallback)
        Uses multiple detection attempts with increasing sensitivity
        
        Returns:
            List of dictionaries with face data
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Try multiple detection configurations (from strict to sensitive)
            configs = [
                {'scaleFactor': 1.1, 'minNeighbors': 5, 'minSize': (30, 30), 'name': 'default'},
                {'scaleFactor': 1.05, 'minNeighbors': 3, 'minSize': (20, 20), 'name': 'sensitive'},
                {'scaleFactor': 1.02, 'minNeighbors': 2, 'minSize': (15, 15), 'name': 'very_sensitive'},
            ]
            
            best_faces = []
            best_config = None
            
            for config in configs:
                faces_rect = self.opencv_cascade.detectMultiScale(
                    gray,
                    scaleFactor=config['scaleFactor'],
                    minNeighbors=config['minNeighbors'],
                    minSize=config['minSize']
                )
                
                if len(faces_rect) > len(best_faces):
                    best_faces = faces_rect
                    best_config = config['name']
                
                # If we found faces, use them
                if len(faces_rect) > 0:
                    break
            
            # If still no faces, try profile cascade
            if len(best_faces) == 0:
                profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
                best_faces = profile_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                if len(best_faces) > 0:
                    best_config = 'profile'
            
            faces = []
            for (x, y, w, h) in best_faces:
                cropped_face = img[y:y+h, x:x+w]
                
                faces.append({
                    'bounding_box': (x, y, w, h),
                    'confidence': 0.8,  # Default confidence for OpenCV
                    'landmarks': {},
                    'cropped_face': cropped_face,
                    'engine': 'opencv',
                    'detection_config': best_config
                })
            
            print(f"✅ OpenCV detected {len(faces)} face(s) using '{best_config}' config")
            return faces
            
        except Exception as e:
            print(f"❌ OpenCV detection error: {e}")
            return []
    
    def detect_faces(self, image_path: str) -> List[Dict]:
        """
        Detect faces using the selected engine
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of face detection results
        """
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return []
        
        # Route to appropriate engine
        if self.engine == 'yolov8':
            return self.detect_faces_yolov8(image_path)
        elif self.engine == 'retinaface':
            return self.detect_faces_retinaface(image_path)
        elif self.engine == 'mtcnn':
            return self.detect_faces_mtcnn(image_path)
        elif self.engine == 'mediapipe':
            return self.detect_faces_mediapipe(image_path)
        elif self.engine == 'opencv':
            return self.detect_faces_opencv(image_path)
        else:
            print(f"⚠️ Unknown engine: {self.engine}, using yolov8 fallback")
            return self.detect_faces_yolov8(image_path) if YOLO_AVAILABLE else self.detect_faces_opencv(image_path)
    
    def detect_faces_auto(self, image_path: str) -> List[Dict]:
        """
        Try all engines and return the best result
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of face detection results from best engine
        """
        engines = ['yolov8', 'retinaface', 'mtcnn', 'mediapipe']
        
        for engine in engines:
            try:
                # Temporarily switch engine
                original_engine = self.engine
                self.engine = engine
                
                faces = self.detect_faces(image_path)
                
                # Restore original engine
                self.engine = original_engine
                
                # Return if faces found
                if faces:
                    print(f"✅ Using {engine} engine - found {len(faces)} face(s)")
                    return faces
                    
            except Exception as e:
                print(f"⚠️ {engine} failed: {e}")
                continue
        
        print("❌ All detection engines failed")
        return []
    
    def crop_and_save_faces(self, image_path: str, output_folder: str) -> List[str]:
        """
        Detect faces, crop them, and save to output folder
        
        Args:
            image_path: Input image path
            output_folder: Folder to save cropped faces
            
        Returns:
            List of saved face image paths
        """
        # Detect faces
        faces = self.detect_faces(image_path)
        
        if not faces:
            print("⚠️ No faces detected")
            return []
        
        # Create output folder
        os.makedirs(output_folder, exist_ok=True)
        
        # Read original image
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        saved_paths = []
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        for i, face in enumerate(faces):
            x, y, w, h = face['bounding_box']
            
            # Crop face
            face_img = img[y:y+h, x:x+w]
            
            # Save cropped face
            output_path = os.path.join(output_folder, f"{base_name}_face_{i}.jpg")
            cv2.imwrite(output_path, face_img)
            saved_paths.append(output_path)
        
        print(f"✅ Saved {len(saved_paths)} cropped face(s) to {output_folder}")
        return saved_paths


# Utility function for easy usage
def detect_faces_simple(image_path: str, engine: str = 'retinaface') -> List[Dict]:
    """
    Simple utility function for face detection
    
    Args:
        image_path: Path to image
        engine: Detection engine to use
        
    Returns:
        List of face detection results
    """
    detector = AdvancedFaceDetector(engine=engine)
    return detector.detect_faces(image_path)
