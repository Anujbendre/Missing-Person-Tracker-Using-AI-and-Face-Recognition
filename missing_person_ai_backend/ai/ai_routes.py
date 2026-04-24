from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import os
import uuid
import shutil
from datetime import datetime

from ai.face_service import recognize_face, recognize_video
from ai.advanced_face_recognition import AdvancedFaceRecognition, recognize_face_in_image

router = APIRouter(
    prefix="/ai",
    tags=["AI Face Recognition"]
)

IMAGE_UPLOAD = "uploads/ai_images"
VIDEO_UPLOAD = "uploads/ai_videos"
OUTPUT_FOLDER = "uploads/recognized"

os.makedirs(IMAGE_UPLOAD, exist_ok=True)
os.makedirs(VIDEO_UPLOAD, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ==================================
# ADVANCED FACE RECOGNITION (CNN-based)
# ==================================

@router.post("/recognize")
async def advanced_recognize(
    image: UploadFile = File(...),
    use_cnn: bool = Form(False)
):
    """
    Advanced face recognition using CNN embeddings
    Returns match results with confidence scores
    """
    try:
        # Generate unique filename
        file_ext = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        file_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(IMAGE_UPLOAD, file_name)
        
        # Save uploaded image
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        print(f"\n🔍 Processing image: {file_name}")
        print(f"📦 Using model: {'CNN' if use_cnn else 'HOG'}")
        
        # Perform face recognition
        results = recognize_face_in_image(file_path, use_cnn=use_cnn)
        
        # Draw bounding boxes on image if matches found
        output_filename = f"result_{file_name}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        if results.get('matches'):
            from ai.advanced_face_recognition import AdvancedFaceRecognition
            recognizer = AdvancedFaceRecognition()
            recognizer.draw_face_boxes(file_path, results['matches'], output_path)
            results['annotated_image'] = f"/uploads/recognized/{output_filename}"
        
        # Add metadata
        results['timestamp'] = datetime.now().isoformat()
        results['original_image'] = f"/uploads/ai_images/{file_name}"
        
        return {
            "status": "success",
            "data": results
        }
        
    except Exception as e:
        print(f"❌ Recognition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================================
# ENCODE DATASET
# ==================================

@router.post("/encode-dataset")
async def encode_dataset():
    """
    Re-encode all missing persons in dataset
    Call this when new persons are added
    """
    try:
        recognizer = AdvancedFaceRecognition()
        encodings = recognizer.encode_missing_persons()
        
        return {
            "status": "success",
            "message": f"Encoded {len(encodings)} persons",
            "total_encoded": len(encodings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================
# VIDEO FACE RECOGNITION
# ==================================

@router.post("/recognize-video")
async def recognize_video_file(video: UploadFile = File(...)):

    file_name = f"{uuid.uuid4()}.mp4"
    file_path = os.path.join(VIDEO_UPLOAD, file_name)

    contents = await video.read()

    with open(file_path, "wb") as f:
        f.write(contents)

    result = recognize_video(file_path)

    return result
