"""
Face Detection and Recognition API Routes
Provides endpoints for:
- Face detection with YOLOv8/RetinaFace/MTCNN/MediaPipe
- Face recognition with DeepFace
- Real-time webcam detection
- Face attribute analysis
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import os
import uuid
import shutil
import cv2
import base64
from typing import Optional
from datetime import datetime

# Import our services
from ai.advanced_face_detection import AdvancedFaceDetector
from ai.deepface_recognition import DeepFaceRecognizer
from ai.mediapipe_detection import MediaPipeFaceDetector

router = APIRouter(prefix="/api/face", tags=["Face Detection & Recognition"])

# Upload folders
UPLOAD_FOLDER = "uploads/face_uploads"
CROPPED_FACES_FOLDER = "uploads/cropped_faces"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CROPPED_FACES_FOLDER, exist_ok=True)


# ==================== MODELS ====================

class DetectionRequest(BaseModel):
    engine: str = "yolov8"  # yolov8, retinaface, mtcnn, mediapipe
    crop_faces: bool = True


class RecognitionRequest(BaseModel):
    model_name: str = "VGG-Face"  # VGG-Face, Facenet, OpenFace, ArcFace
    threshold: int = 70


class AnalysisRequest(BaseModel):
    analyze_attributes: bool = True


# ==================== FACE DETECTION ENDPOINTS ====================

@router.post("/detect-face")
async def detect_face(
    file: UploadFile = File(...),
    engine: str = Form("yolov8"),
    crop_faces: bool = Form(True)
):
    """
    Detect faces in uploaded image
    
    Args:
        file: Image file
        engine: Detection engine (yolov8, retinaface, mtcnn, mediapipe)
        crop_faces: Whether to crop and save detected faces
    
    Returns:
        Detection results with bounding boxes and confidence
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type not allowed. Use: {allowed_extensions}")
        
        # Generate unique filename
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Image saved: {file_path}")
        
        # Initialize detector
        detector = AdvancedFaceDetector(engine=engine)
        
        # Detect faces
        faces = detector.detect_faces(file_path)
        
        if not faces:
            return {
                "status": "success",
                "message": "No faces detected",
                "total_faces": 0,
                "faces": [],
                "image_path": f"/uploads/face_uploads/{unique_filename}"
            }
        
        # Crop and save faces if requested
        cropped_paths = []
        if crop_faces:
            cropped_paths = detector.crop_and_save_faces(file_path, CROPPED_FACES_FOLDER)
        
        # Prepare response (remove numpy arrays)
        faces_response = []
        for i, face in enumerate(faces):
            # Convert numpy ints to Python ints
            bbox = face['bounding_box']
            face_data = {
                "face_index": i,
                "bounding_box": {
                    "x": int(bbox[0]),
                    "y": int(bbox[1]),
                    "width": int(bbox[2]),
                    "height": int(bbox[3])
                },
                "confidence": float(face['confidence']),
                "engine": face['engine']
            }
            
            # Add detection config if available
            if 'detection_config' in face:
                face_data["detection_config"] = face['detection_config']
            
            # Add cropped face path if available
            if i < len(cropped_paths):
                face_data["cropped_face_path"] = cropped_paths[i]
            
            faces_response.append(face_data)
        
        return {
            "status": "success",
            "message": f"Detected {len(faces)} face(s)",
            "total_faces": len(faces),
            "faces": faces_response,
            "image_path": f"/uploads/face_uploads/{unique_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Face detection error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-multiple")
async def detect_multiple_faces(
    files: list[UploadFile] = File(...),
    engine: str = Form("yolov8")
):
    """
    Detect faces in multiple images
    
    Args:
        files: List of image files
        engine: Detection engine
    
    Returns:
        Detection results for all images
    """
    results = []
    
    for file in files:
        try:
            # Save file
            file_ext = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Detect faces
            detector = AdvancedFaceDetector(engine=engine)
            faces = detector.detect_faces(file_path)
            
            results.append({
                "filename": file.filename,
                "image_path": f"/uploads/face_uploads/{unique_filename}",
                "total_faces": len(faces),
                "faces": len(faces)
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "status": "success",
        "total_images": len(results),
        "results": results
    }


# ==================== FACE RECOGNITION ENDPOINTS ====================

@router.post("/recognize-face")
async def recognize_face(
    file: UploadFile = File(...),
    model_name: str = Form("VGG-Face"),
    threshold: int = Form(70)
):
    """
    Recognize face by comparing with database
    Uses DeepFace if available, otherwise uses OpenCV fallback
    """
    try:
        from ai.deepface_recognition import DeepFaceRecognizer, DEEPFACE_AVAILABLE
        import cv2
        import numpy as np
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Save uploaded file
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Image saved for recognition: {file_path}")
        
        # Try DeepFace first
        if DEEPFACE_AVAILABLE:
            print("🔍 Using DeepFace for recognition...")
            try:
                recognizer = DeepFaceRecognizer(model_name=model_name)
                recognizer.load_encodings()
                
                if not recognizer.known_faces_db:
                    db_path = "dataset/missing_persons"
                    if os.path.exists(db_path):
                        count = recognizer.load_known_faces(db_path)
                        recognizer.save_encodings()
                
                matches = recognizer.find_matches(file_path, threshold)
                
                if matches:
                    best_match = matches[0]
                    return {
                        "status": "success",
                        "match_found": True,
                        "person_id": best_match['person_id'],
                        "name": best_match['name'],
                        "match_percentage": best_match['match_percentage'],
                        "confidence": best_match['match_percentage'],
                        "method": "DeepFace",
                        "all_matches": matches[:5],
                        "image_path": f"/uploads/face_uploads/{unique_filename}"
                    }
                else:
                    return {
                        "status": "success",
                        "match_found": False,
                        "message": "No match found in database",
                        "method": "DeepFace",
                        "image_path": f"/uploads/face_uploads/{unique_filename}"
                    }
            except Exception as e:
                print(f"⚠️ DeepFace failed: {e}, falling back to OpenCV")
        
        # OpenCV Fallback Recognition
        print("🔍 Using OpenCV for recognition (fallback)...")
        return await _opencv_fallback_recognition(file_path, unique_filename, threshold)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Face recognition error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def _opencv_fallback_recognition(file_path: str, unique_filename: str, threshold: int):
    """OpenCV-based face recognition fallback"""
    import cv2
    import numpy as np
    
    try:
        # Load query image
        query_img = cv2.imread(file_path)
        if query_img is None:
            raise HTTPException(status_code=400, detail="Could not load uploaded image")
        
        query_gray = cv2.cvtColor(query_img, cv2.COLOR_BGR2GRAY)
        
        # Detect face in query image
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        query_faces = cascade.detectMultiScale(query_gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20))
        
        if len(query_faces) == 0:
            return {
                "status": "success",
                "match_found": False,
                "message": "No face detected in uploaded image",
                "method": "OpenCV"
            }
        
        # Extract query face
        qx, qy, qw, qh = query_faces[0]
        query_face = query_gray[qy:qy+qh, qx:qx+qw]
        query_face_resized = cv2.resize(query_face, (100, 100))
        query_face_hist = cv2.calcHist([query_face_resized], [0], None, [256], [0, 256])
        cv2.normalize(query_face_hist, query_face_hist)
        
        # Compare with database
        db_path = "dataset/missing_persons"
        if not os.path.exists(db_path):
            return {
                "status": "success",
                "match_found": False,
                "message": "Database folder not found",
                "method": "OpenCV"
            }
        
        best_match = None
        best_accuracy = 0
        
        for filename in os.listdir(db_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                db_img_path = os.path.join(db_path, filename)
                
                # Load database image
                db_img = cv2.imread(db_img_path)
                if db_img is None:
                    continue
                
                db_gray = cv2.cvtColor(db_img, cv2.COLOR_BGR2GRAY)
                
                # Detect face
                db_faces = cascade.detectMultiScale(db_gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20))
                
                if len(db_faces) == 0:
                    continue
                
                # Extract face
                dx, dy, dw, dh = db_faces[0]
                db_face = db_gray[dy:dy+dh, dx:dx+dw]
                db_face_resized = cv2.resize(db_face, (100, 100))
                
                # Calculate histogram
                db_face_hist = cv2.calcHist([db_face_resized], [0], None, [256], [0, 256])
                cv2.normalize(db_face_hist, db_face_hist)
                
                # Compare
                similarity = cv2.compareHist(query_face_hist, db_face_hist, cv2.HISTCMP_CORREL)
                accuracy = max(0, (similarity + 1) * 50)
                
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    person_id = filename.split('.')[0]
                    best_match = {
                        "person_id": person_id,
                        "name": person_id.replace('_', ' ').title(),
                        "match_percentage": round(accuracy, 2),
                        "image_path": f"dataset/missing_persons/{filename}"
                    }
        
        if best_match and best_accuracy >= threshold:
            return {
                "status": "success",
                "match_found": True,
                "person_id": best_match['person_id'],
                "name": best_match['name'],
                "match_percentage": best_match['match_percentage'],
                "confidence": best_match['match_percentage'],
                "method": "OpenCV (Histogram)",
                "image_path": f"/uploads/face_uploads/{unique_filename}"
            }
        else:
            return {
                "status": "success",
                "match_found": False,
                "message": f"No match found above {threshold}% threshold (best: {best_accuracy:.2f}%)",
                "method": "OpenCV",
                "best_match": best_match,
                "image_path": f"/uploads/face_uploads/{unique_filename}"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ OpenCV recognition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-faces")
async def verify_faces(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    model_name: str = Form("VGG-Face")
):
    """
    Verify if two faces belong to the same person
    
    Args:
        file1: First image
        file2: Second image
        model_name: Recognition model
    
    Returns:
        Verification result
    """
    try:
        # Save both files
        file_ext1 = os.path.splitext(file1.filename)[1].lower()
        file_ext2 = os.path.splitext(file2.filename)[1].lower()
        
        unique_filename1 = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_1_{uuid.uuid4().hex[:8]}{file_ext1}"
        unique_filename2 = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_2_{uuid.uuid4().hex[:8]}{file_ext2}"
        
        file_path1 = os.path.join(UPLOAD_FOLDER, unique_filename1)
        file_path2 = os.path.join(UPLOAD_FOLDER, unique_filename2)
        
        with open(file_path1, "wb") as buffer:
            shutil.copyfileobj(file1.file, buffer)
        
        with open(file_path2, "wb") as buffer:
            shutil.copyfileobj(file2.file, buffer)
        
        # Verify faces
        recognizer = DeepFaceRecognizer(model_name=model_name)
        result = recognizer.verify_faces(file_path1, file_path2)
        
        return {
            "status": "success",
            "verified": result.get('verified', False),
            "match_percentage": result.get('match_percentage', 0),
            "distance": result.get('distance', 0),
            "threshold": result.get('threshold', 0)
        }
        
    except Exception as e:
        print(f"❌ Face verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FACE ANALYSIS ENDPOINTS ====================

@router.post("/analyze-face")
async def analyze_face(
    file: UploadFile = File(...),
    analyze_attributes: bool = Form(True)
):
    """
    Analyze face attributes (age, gender, emotion, race)
    
    Args:
        file: Image file
        analyze_attributes: Whether to analyze attributes
    
    Returns:
        Face attributes
    """
    try:
        # Save file
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analyze face
        recognizer = DeepFaceRecognizer()
        attributes = recognizer.analyze_face(file_path)
        
        return {
            "status": "success",
            "attributes": attributes,
            "image_path": f"/uploads/face_uploads/{unique_filename}"
        }
        
    except Exception as e:
        print(f"❌ Face analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MEDIAPIPE REAL-TIME ENDPOINTS ====================

@router.post("/mediapipe-detect")
async def mediapipe_detect_face(
    file: UploadFile = File(...),
    return_annotated: bool = Form(True)
):
    """
    Detect faces using MediaPipe
    
    Args:
        file: Image file
        return_annotated: Whether to return annotated image
    
    Returns:
        Detection results
    """
    try:
        # Save file
        file_ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Detect faces with MediaPipe
        detector = MediaPipeFaceDetector()
        faces = detector.detect_faces_from_image(file_path)
        
        response = {
            "status": "success",
            "total_faces": len(faces),
            "faces": faces,
            "image_path": f"/uploads/face_uploads/{unique_filename}"
        }
        
        # Return annotated image if requested
        if return_annotated and faces:
            # Read image and draw faces
            img = cv2.imread(file_path)
            annotated_img = detector.draw_faces_on_frame(img, faces)
            
            # Save annotated image
            annotated_filename = f"annotated_{unique_filename}"
            annotated_path = os.path.join(UPLOAD_FOLDER, annotated_filename)
            cv2.imwrite(annotated_path, annotated_img)
            
            response["annotated_image_path"] = f"/uploads/face_uploads/{annotated_filename}"
        
        return response
        
    except Exception as e:
        print(f"❌ MediaPipe detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webcam-stream")
async def webcam_stream(camera_id: int = 0):
    """
    Stream webcam feed with face detection (SSE)
    
    Args:
        camera_id: Camera device ID
    
    Returns:
        Video stream with face detection
    """
    try:
        detector = MediaPipeFaceDetector()
        
        def generate_frames():
            cap = cv2.VideoCapture(camera_id)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open camera {camera_id}")
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Detect faces
                    faces = detector.detect_faces_from_frame(frame)
                    
                    # Draw faces
                    annotated_frame = detector.draw_faces_on_frame(frame, faces)
                    
                    # Encode as JPEG
                    _, buffer = cv2.imencode('.jpg', annotated_frame)
                    frame_bytes = buffer.tobytes()
                    
                    # Yield frame
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            finally:
                cap.release()
        
        return StreamingResponse(
            generate_frames(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DATABASE MANAGEMENT ENDPOINTS ====================

@router.post("/load-database")
async def load_face_database(
    database_path: str = Form("dataset/missing_persons"),
    model_name: str = Form("VGG-Face")
):
    """
    Load face database for recognition
    
    Args:
        database_path: Path to folder with face images
        model_name: Recognition model
    
    Returns:
        Loading status
    """
    try:
        if not os.path.exists(database_path):
            raise HTTPException(status_code=404, detail=f"Database path not found: {database_path}")
        
        recognizer = DeepFaceRecognizer(model_name=model_name)
        count = recognizer.load_known_faces(database_path)
        recognizer.save_encodings()
        
        return {
            "status": "success",
            "message": f"Loaded {count} faces from database",
            "total_faces": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Database loading error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-encodings")
async def save_encodings(model_name: str = Form("VGG-Face")):
    """
    Save face encodings to file
    
    Returns:
        Save status
    """
    try:
        recognizer = DeepFaceRecognizer(model_name=model_name)
        recognizer.load_encodings()
        recognizer.save_encodings()
        
        return {
            "status": "success",
            "message": "Encodings saved successfully"
        }
        
    except Exception as e:
        print(f"❌ Error saving encodings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== UTILITY ENDPOINTS ====================

@router.get("/supported-models")
async def get_supported_models():
    """
    Get list of supported detection and recognition models
    
    Returns:
        Available models
    """
    return {
        "detection_engines": ["yolov8", "retinaface", "mtcnn", "mediapipe", "opencv"],
        "recognition_models": ["VGG-Face", "Facenet", "OpenFace", "ArcFace", "DeepID"],
        "analysis_attributes": ["age", "gender", "emotion", "race"]
    }
