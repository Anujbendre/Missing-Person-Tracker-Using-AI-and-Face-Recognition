"""
Advanced Face Recognition Service using DeepFace
Supports multiple backends:
- VGG-Face
- Facenet
- OpenFace
- ArcFace
"""

import cv2
import numpy as np
import os
from typing import List, Dict, Optional, Tuple
import json

# Try to import DeepFace with fallback
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False
    print("⚠️ DeepFace not available, face recognition will use fallback methods")


class DeepFaceRecognizer:
    """Face recognition using DeepFace library"""
    
    def __init__(self, model_name: str = 'VGG-Face'):
        """
        Initialize DeepFace recognizer
        
        Args:
            model_name: Face recognition model ('VGG-Face', 'Facenet', 'OpenFace', 'ArcFace')
        """
        self.model_name = model_name
        self.known_faces_db = {}  # {person_id: {'encoding': np.array, 'name': str, 'image_path': str}}
        self.encodings_file = "dataset/deepface_encodings.json"
        
        print(f"✅ DeepFaceRecognizer initialized with model: {model_name}")
    
    def extract_face_encoding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Extract face encoding/embedding using DeepFace
        
        Args:
            image_path: Path to image file
            
        Returns:
            Face encoding as numpy array or None
        """
        if not DEEPFACE_AVAILABLE:
            print("❌ DeepFace not available")
            return None
        
        try:
            # DeepFace represent function extracts embedding
            embedding_objs = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                enforce_detection=False
            )
            
            if embedding_objs and len(embedding_objs) > 0:
                # Return the first face's embedding
                embedding = embedding_objs[0]['embedding']
                return np.array(embedding)
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting encoding: {e}")
            return None
    
    def verify_faces(self, image1_path: str, image2_path: str) -> Dict:
        """
        Verify if two faces belong to the same person
        
        Args:
            image1_path: First image path
            image2_path: Second image path
            
        Returns:
            Dictionary with verification result
        """
        if not DEEPFACE_AVAILABLE:
            return {
                'verified': False,
                'error': 'DeepFace not available'
            }
        
        try:
            result = DeepFace.verify(
                img1_path=image1_path,
                img2_path=image2_path,
                model_name=self.model_name,
                enforce_detection=False
            )
            
            return {
                'verified': result['verified'],
                'distance': result['distance'],
                'threshold': result['threshold'],
                'match_percentage': round((1 - result['distance'] / result['threshold']) * 100, 2)
            }
            
        except Exception as e:
            print(f"❌ Face verification error: {e}")
            return {
                'verified': False,
                'error': str(e)
            }
    
    def find_matches(self, image_path: str, threshold: int = 70) -> List[Dict]:
        """
        Find matching faces from known database
        
        Args:
            image_path: Query image path
            threshold: Match threshold (0-100)
            
        Returns:
            List of matches with confidence scores
        """
        if not self.known_faces_db:
            print("⚠️ No known faces in database. Call load_known_faces() first.")
            return []
        
        try:
            # Extract encoding from query image
            query_embedding = self.extract_face_encoding(image_path)
            
            if query_embedding is None:
                print("❌ Could not extract encoding from query image")
                return []
            
            matches = []
            
            # Compare with all known faces
            for person_id, face_data in self.known_faces_db.items():
                known_embedding = face_data['encoding']
                
                # Calculate cosine similarity
                similarity = self.cosine_similarity(query_embedding, known_embedding)
                match_percentage = round(similarity * 100, 2)
                
                if match_percentage >= threshold:
                    matches.append({
                        'person_id': person_id,
                        'name': face_data['name'],
                        'match_percentage': match_percentage,
                        'image_path': face_data['image_path'],
                        'distance': float(1 - similarity)
                    })
            
            # Sort by match percentage (highest first)
            matches.sort(key=lambda x: x['match_percentage'], reverse=True)
            
            print(f"✅ Found {len(matches)} match(es) above {threshold}% threshold")
            return matches
            
        except Exception as e:
            print(f"❌ Match finding error: {e}")
            return []
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
    
    def analyze_face(self, image_path: str) -> Dict:
        """
        Analyze face attributes (age, gender, emotion, race)
        
        Args:
            image_path: Path to image
            
        Returns:
            Dictionary with face attributes
        """
        if not DEEPFACE_AVAILABLE:
            return {'error': 'DeepFace not available'}
        
        try:
            result = DeepFace.analyze(
                img_path=image_path,
                actions=['age', 'gender', 'emotion', 'race'],
                enforce_detection=False
            )
            
            # Result might be a list if multiple faces
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            
            return {
                'age': result.get('age', 'Unknown'),
                'gender': result.get('dominant_gender', 'Unknown'),
                'emotion': result.get('dominant_emotion', 'Unknown'),
                'race': result.get('dominant_race', 'Unknown'),
                'emotion_scores': result.get('emotion', {}),
                'race_scores': result.get('race', {})
            }
            
        except Exception as e:
            print(f"❌ Face analysis error: {e}")
            return {'error': str(e)}
    
    def load_known_faces(self, database_path: str = "dataset/missing_persons") -> int:
        """
        Load known faces from database folder
        
        Args:
            database_path: Path to folder containing person images
            
        Returns:
            Number of loaded faces
        """
        if not os.path.exists(database_path):
            print(f"❌ Database path not found: {database_path}")
            return 0
        
        count = 0
        
        # Process each image file
        for filename in os.listdir(database_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = os.path.join(database_path, filename)
                
                # Extract person ID and name from filename
                # Expected format: person_101.jpg or name_person_101.jpg
                base_name = os.path.splitext(filename)[0]
                person_id = base_name
                name = base_name.replace('_', ' ').title()
                
                try:
                    # Extract encoding
                    embedding = self.extract_face_encoding(image_path)
                    
                    if embedding is not None:
                        self.known_faces_db[person_id] = {
                            'encoding': embedding,
                            'name': name,
                            'image_path': image_path
                        }
                        count += 1
                        print(f"  ✅ Loaded {person_id}")
                    else:
                        print(f"  ⚠️ No face found in {filename}")
                        
                except Exception as e:
                    print(f"  ❌ Error loading {filename}: {e}")
        
        print(f"✅ Loaded {count} known faces")
        return count
    
    def save_encodings(self):
        """Save encodings to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.encodings_file), exist_ok=True)
            
            # Convert numpy arrays to lists for JSON serialization
            data_to_save = {}
            for person_id, face_data in self.known_faces_db.items():
                data_to_save[person_id] = {
                    'name': face_data['name'],
                    'image_path': face_data['image_path'],
                    'encoding': face_data['encoding'].tolist()
                }
            
            with open(self.encodings_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            
            print(f"💾 Encodings saved to {self.encodings_file}")
            
        except Exception as e:
            print(f"❌ Error saving encodings: {e}")
    
    def load_encodings(self):
        """Load encodings from JSON file"""
        try:
            if os.path.exists(self.encodings_file):
                with open(self.encodings_file, 'r') as f:
                    data = json.load(f)
                
                # Convert lists back to numpy arrays
                for person_id, face_data in data.items():
                    self.known_faces_db[person_id] = {
                        'name': face_data['name'],
                        'image_path': face_data['image_path'],
                        'encoding': np.array(face_data['encoding'])
                    }
                
                print(f"✅ Loaded {len(self.known_faces_db)} encodings from file")
            else:
                print("📝 No pre-saved encodings found")
                
        except Exception as e:
            print(f"❌ Error loading encodings: {e}")


# Utility functions
def recognize_face_deepface(image_path: str, model: str = 'VGG-Face', threshold: int = 70) -> Dict:
    """
    Simple utility to recognize a face
    
    Args:
        image_path: Query image path
        model: Recognition model to use
        threshold: Match threshold
        
    Returns:
        Recognition result dictionary
    """
    recognizer = DeepFaceRecognizer(model_name=model)
    
    # Try to load pre-saved encodings
    recognizer.load_encodings()
    
    # If no encodings loaded, try to load from database
    if not recognizer.known_faces_db:
        recognizer.load_known_faces()
        recognizer.save_encodings()
    
    # Find matches
    matches = recognizer.find_matches(image_path, threshold)
    
    if matches:
        best_match = matches[0]
        return {
            'match_found': True,
            'person_id': best_match['person_id'],
            'name': best_match['name'],
            'match_percentage': best_match['match_percentage'],
            'all_matches': matches[:5]  # Top 5 matches
        }
    else:
        return {
            'match_found': False,
            'message': 'No match found'
        }


def analyze_face_attributes(image_path: str) -> Dict:
    """
    Analyze face attributes
    
    Args:
        image_path: Path to image
        
    Returns:
        Face attributes dictionary
    """
    recognizer = DeepFaceRecognizer()
    return recognizer.analyze_face(image_path)
