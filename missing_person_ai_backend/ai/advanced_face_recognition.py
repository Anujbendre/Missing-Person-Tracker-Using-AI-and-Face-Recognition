"""
Advanced Face Recognition System
Uses CNN-based feature extraction and embedding-based matching
Research-based approach with OpenCV, dlib, and face_recognition libraries
"""

import cv2
import numpy as np
import face_recognition
import os
from typing import List, Tuple, Dict, Optional
import pickle
from datetime import datetime


class AdvancedFaceRecognition:
    """
    Production-grade face recognition system using:
    - HOG/CNN face detection (dlib)
    - Deep learning-based face embeddings (128-d vectors)
    - Euclidean distance for similarity matching
    """
    
    def __init__(self, model: str = 'hog'):
        """
        Initialize face recognition system
        
        Args:
            model: 'hog' (faster) or 'cnn' (more accurate)
        """
        self.model = model
        self.known_encodings = {}  # {person_id: encoding}
        self.known_persons = {}    # {person_id: person_info}
        self.dataset_path = "dataset/missing_persons"
        self.encodings_file = "dataset/encodings.pkl"
        
        # Load pre-computed encodings if available
        self.load_encodings()
    
    def detect_faces(self, image_path: str) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using HOG or CNN-based detector
        
        Returns:
            List of face locations as (top, right, bottom, left)
        """
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Detect faces using specified model
            face_locations = face_recognition.face_locations(
                image, 
                model=self.model
            )
            
            print(f"✅ Detected {len(face_locations)} face(s) in {image_path}")
            return face_locations
            
        except Exception as e:
            print(f"❌ Error detecting faces: {e}")
            return []
    
    def extract_face_encoding(self, image_path: str, face_location: Optional[Tuple] = None) -> Optional[np.ndarray]:
        """
        Extract 128-dimensional face embedding using pre-trained CNN
        
        Args:
            image_path: Path to image
            face_location: Optional (top, right, bottom, left)
            
        Returns:
            128-d face encoding vector or None
        """
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Extract encoding
            encodings = face_recognition.face_encodings(
                image,
                known_face_locations=[face_location] if face_location else None,
                model='large'  # More accurate model
            )
            
            if len(encodings) > 0:
                return encodings[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting encoding: {e}")
            return None
    
    def encode_missing_persons(self) -> Dict:
        """
        Encode all missing person images in dataset
        Builds lookup table of known faces
        """
        print("🔄 Encoding missing persons dataset...")
        
        self.known_encodings = {}
        self.known_persons = {}
        
        if not os.path.exists(self.dataset_path):
            print(f"⚠️ Dataset folder not found: {self.dataset_path}")
            return self.known_encodings
        
        # Process each image file
        for filename in os.listdir(self.dataset_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(self.dataset_path, filename)
                
                # Extract person_id from filename (e.g., person_101.jpg -> 101)
                person_id = filename.split('.')[0].replace('person_', '')
                
                try:
                    # Extract face encoding
                    encoding = self.extract_face_encoding(image_path)
                    
                    if encoding is not None:
                        self.known_encodings[person_id] = encoding
                        self.known_persons[person_id] = {
                            'person_id': person_id,
                            'image_path': image_path,
                            'filename': filename
                        }
                        print(f"  ✅ Encoded person_{person_id}")
                    else:
                        print(f"  ⚠️ No face found in {filename}")
                        
                except Exception as e:
                    print(f"  ❌ Error encoding {filename}: {e}")
        
        # Save encodings for future use
        self.save_encodings()
        
        print(f"✅ Successfully encoded {len(self.known_encodings)} persons")
        return self.known_encodings
    
    def save_encodings(self):
        """Save pre-computed encodings to disk"""
        try:
            os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
            
            data = {
                'encodings': self.known_encodings,
                'persons': self.known_persons,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            
            print(f"💾 Encodings saved to {self.encodings_file}")
            
        except Exception as e:
            print(f"❌ Error saving encodings: {e}")
    
    def load_encodings(self):
        """Load pre-computed encodings from disk"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                
                self.known_encodings = data.get('encodings', {})
                self.known_persons = data.get('persons', {})
                
                print(f"✅ Loaded {len(self.known_encodings)} pre-computed encodings")
            else:
                print("📝 No pre-computed encodings found")
                
        except Exception as e:
            print(f"❌ Error loading encodings: {e}")
            self.known_encodings = {}
            self.known_persons = {}
    
    def compare_faces_euclidean(self, encoding1: np.ndarray, encoding2: np.ndarray) -> Tuple[float, float]:
        """
        Compare two face encodings using Euclidean distance
        
        Returns:
            (distance, confidence_percentage)
            - Lower distance = better match
            - Distance < 0.6 is typically a match
        """
        # Calculate Euclidean distance
        distance = np.linalg.norm(encoding1 - encoding2)
        
        # Convert to confidence percentage
        # Distance 0.0 = 100% match, Distance 1.0 = 0% match
        confidence = max(0, min(100, (1.0 - distance) * 100))
        
        return distance, confidence
    
    def recognize_face(self, image_path: str) -> Dict:
        """
        Recognize face(s) in image by comparing with known encodings
        
        Returns:
            Dictionary with match results
        """
        results = {
            'matches': [],
            'total_faces': 0,
            'processing_time': 0
        }
        
        start_time = datetime.now()
        
        try:
            # Detect faces in query image
            face_locations = self.detect_faces(image_path)
            results['total_faces'] = len(face_locations)
            
            if len(face_locations) == 0:
                print("⚠️ No faces detected in query image")
                return results
            
            # Extract encoding for each detected face
            for i, face_location in enumerate(face_locations):
                query_encoding = self.extract_face_encoding(image_path, face_location)
                
                if query_encoding is None:
                    continue
                
                # Compare with all known encodings
                best_match = None
                best_distance = float('inf')
                best_confidence = 0
                
                for person_id, known_encoding in self.known_encodings.items():
                    distance, confidence = self.compare_faces_euclidean(
                        query_encoding, 
                        known_encoding
                    )
                    
                    # Keep track of best match
                    if distance < best_distance:
                        best_distance = distance
                        best_confidence = confidence
                        best_match = person_id
                
                # Determine if match is valid (threshold: 0.6)
                is_match = best_distance < 0.6
                
                match_result = {
                    'face_index': i,
                    'face_location': face_location,  # (top, right, bottom, left)
                    'match_found': is_match,
                    'person_id': best_match if is_match else None,
                    'confidence': round(best_confidence, 2),
                    'distance': round(best_distance, 4),
                    'person_info': self.known_persons.get(best_match, {}) if is_match else None
                }
                
                results['matches'].append(match_result)
                
                if is_match:
                    print(f"✅ Match found: person_{best_match} ({best_confidence:.2f}%)")
                else:
                    print(f"❌ No match (best: {best_confidence:.2f}%)")
            
            # Calculate processing time
            end_time = datetime.now()
            results['processing_time'] = (end_time - start_time).total_seconds()
            
        except Exception as e:
            print(f"❌ Error in recognition: {e}")
            results['error'] = str(e)
        
        return results
    
    def draw_face_boxes(self, image_path: str, matches: List[Dict], output_path: str):
        """
        Draw bounding boxes and labels on image
        
        Args:
            image_path: Input image
            matches: List of match results
            output_path: Output image path
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            
            for match in matches:
                top, right, bottom, left = match['face_location']
                
                # Choose color based on match result
                if match['match_found']:
                    color = (0, 255, 0)  # Green for match
                    label = f"Match: {match['person_id']} ({match['confidence']}%)"
                else:
                    color = (0, 0, 255)  # Red for no match
                    label = f"No Match ({match['confidence']}%)"
                
                # Draw rectangle
                cv2.rectangle(image, (left, top), (right, bottom), color, 3)
                
                # Draw label background
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(image, (left, top - 30), (left + label_size[0], top), color, -1)
                
                # Draw text
                cv2.putText(
                    image, 
                    label, 
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, 
                    (255, 255, 255), 
                    2
                )
            
            # Save output image
            cv2.imwrite(output_path, image)
            print(f"✅ Annotated image saved to {output_path}")
            
        except Exception as e:
            print(f"❌ Error drawing face boxes: {e}")


# Utility function for API usage
def recognize_face_in_image(image_path: str, use_cnn: bool = False) -> Dict:
    """
    Standalone function to recognize faces in an image
    
    Args:
        image_path: Path to query image
        use_cnn: Use CNN model (more accurate but slower)
        
    Returns:
        Recognition results dictionary
    """
    # Initialize recognizer
    model = 'cnn' if use_cnn else 'hog'
    recognizer = AdvancedFaceRecognition(model=model)
    
    # Encode dataset if not already done
    if len(recognizer.known_encodings) == 0:
        recognizer.encode_missing_persons()
    
    # Recognize faces
    results = recognizer.recognize_face(image_path)
    
    return results
