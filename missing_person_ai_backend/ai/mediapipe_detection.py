"""
MediaPipe Real-Time Face Detection Service
Optimized for webcam/video stream processing
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Generator
import base64

# Try to import MediaPipe with fallback
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe not available")


class MediaPipeFaceDetector:
    """Real-time face detection using MediaPipe"""
    
    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        """
        Initialize MediaPipe face detector
        
        Args:
            min_detection_confidence: Minimum detection confidence (0-1)
            min_tracking_confidence: Minimum tracking confidence (0-1)
        """
        if not MEDIAPIPE_AVAILABLE:
            print("⚠️ MediaPipe not available, using OpenCV fallback")
            # Initialize OpenCV fallback
            self.opencv_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.use_opencv = True
            return
        
        self.use_opencv = False
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        print("✅ MediaPipeFaceDetector initialized")
    
    def detect_faces_from_image(self, image_path: str) -> List[Dict]:
        """
        Detect faces from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of face detection results
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            return self.detect_faces_from_frame(image)
            
        except Exception as e:
            print(f"❌ Error detecting faces from image: {e}")
            return []
    
    def detect_faces_from_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect faces from video frame (numpy array)
        
        Args:
            frame: BGR image frame
            
        Returns:
            List of face detection results
        """
        # Use OpenCV fallback if MediaPipe not available
        if self.use_opencv:
            return self._detect_faces_opencv(frame)
        
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame
            results = self.face_detection.process(rgb_frame)
            
            faces = []
            height, width, _ = frame.shape
            
            if results.detections:
                for idx, detection in enumerate(results.detections):
                    # Extract bounding box
                    bboxC = detection.location_data.relative_bounding_box
                    
                    x = int(bboxC.xmin * width)
                    y = int(bboxC.ymin * height)
                    w = int(bboxC.width * width)
                    h = int(bboxC.height * height)
                    
                    # Ensure coordinates are within bounds
                    x = max(0, x)
                    y = max(0, y)
                    x2 = min(width, x + w)
                    y2 = min(height, y + h)
                    
                    # Crop face
                    cropped_face = frame[y:y2, x:x2]
                    
                    # Get confidence score
                    confidence = detection.score[0] if detection.score else 0.0
                    
                    faces.append({
                        'face_index': idx,
                        'bounding_box': {'x': x, 'y': y, 'width': w, 'height': h},
                        'confidence': float(confidence),
                        'cropped_face': cropped_face
                    })
            
            return faces
            
        except Exception as e:
            print(f"❌ Error detecting faces from frame: {e}")
            return []
    
    def _detect_faces_opencv(self, frame: np.ndarray) -> List[Dict]:
        """OpenCV fallback detection with multiple sensitivity levels"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Try multiple configurations
            configs = [
                {'scaleFactor': 1.1, 'minNeighbors': 5, 'minSize': (30, 30)},
                {'scaleFactor': 1.05, 'minNeighbors': 3, 'minSize': (20, 20)},
                {'scaleFactor': 1.02, 'minNeighbors': 2, 'minSize': (15, 15)},
            ]
            
            best_faces = []
            
            for config in configs:
                faces_rect = self.opencv_cascade.detectMultiScale(
                    gray,
                    scaleFactor=config['scaleFactor'],
                    minNeighbors=config['minNeighbors'],
                    minSize=config['minSize']
                )
                
                if len(faces_rect) > len(best_faces):
                    best_faces = faces_rect
                
                if len(faces_rect) > 0:
                    break
            
            faces = []
            for idx, (x, y, w, h) in enumerate(best_faces):
                faces.append({
                    'face_index': idx,
                    'bounding_box': {'x': x, 'y': y, 'width': w, 'height': h},
                    'confidence': 0.8,
                    'cropped_face': frame[y:y+h, x:x+w]
                })
            
            return faces
        except Exception as e:
            print(f"❌ OpenCV detection error: {e}")
            return []
    
    def draw_faces_on_frame(self, frame: np.ndarray, faces: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Original BGR frame
            faces: List of face detection results
            
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        for face in faces:
            bbox = face['bounding_box']
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            confidence = face['confidence']
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Draw label background
            label = f"Face: {confidence:.2%}"
            label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            cv2.rectangle(
                annotated_frame,
                (x, y - label_size[1] - 10),
                (x + label_size[0], y),
                (0, 255, 0),
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated_frame,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )
        
        return annotated_frame
    
    def process_webcam_stream(self, camera_id: int = 0) -> Generator[bytes, None, None]:
        """
        Generator function for webcam stream processing
        
        Args:
            camera_id: Camera device ID
            
        Yields:
            JPEG encoded frames with face detections
        """
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open camera {camera_id}")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect faces
                faces = self.detect_faces_from_frame(frame)
                
                # Draw faces
                annotated_frame = self.draw_faces_on_frame(frame, faces)
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', annotated_frame)
                frame_bytes = buffer.tobytes()
                
                yield frame_bytes
                
        finally:
            cap.release()
    
    def process_video_file(self, video_path: str, output_path: str) -> Dict:
        """
        Process video file and detect faces
        
        Args:
            video_path: Input video path
            output_path: Output video path
            
        Returns:
            Processing statistics
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        stats = {
            'total_frames': total_frames,
            'frames_processed': 0,
            'faces_detected': 0,
            'fps': fps
        }
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect faces
                faces = self.detect_faces_from_frame(frame)
                stats['frames_processed'] += 1
                stats['faces_detected'] += len(faces)
                
                # Draw faces
                annotated_frame = self.draw_faces_on_frame(frame, faces)
                out.write(annotated_frame)
                
        finally:
            cap.release()
            out.release()
        
        print(f"✅ Video processed: {stats['faces_detected']} faces in {stats['frames_processed']} frames")
        return stats
    
    def frame_to_base64(self, frame: np.ndarray) -> str:
        """
        Convert frame to base64 string
        
        Args:
            frame: BGR image frame
            
        Returns:
            Base64 encoded string
        """
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    
    def base64_to_frame(self, base64_str: str) -> np.ndarray:
        """
        Convert base64 string to frame
        
        Args:
            base64_str: Base64 encoded image
            
        Returns:
            BGR image frame
        """
        img_bytes = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


# Utility functions
def detect_faces_mediapipe(image_path: str) -> List[Dict]:
    """
    Simple utility for MediaPipe face detection
    
    Args:
        image_path: Path to image
        
    Returns:
        List of face detection results
    """
    detector = MediaPipeFaceDetector()
    return detector.detect_faces_from_image(image_path)


def process_video_with_faces(video_path: str, output_path: str) -> Dict:
    """
    Process video and detect faces
    
    Args:
        video_path: Input video
        output_path: Output video
        
    Returns:
        Processing statistics
    """
    detector = MediaPipeFaceDetector()
    return detector.process_video_file(video_path, output_path)
