"""
YOLO Face Detection - Quick Start Examples
Shows how to use the new YOLO integration in your Missing Person Tracking System
"""

# ========================================
# EXAMPLE 1: Basic YOLO Face Detection
# ========================================
from ai.yolo_face_detection import YOLOFaceDetector

# Initialize YOLO detector (nano model - fastest)
detector = YOLOFaceDetector(model_size='n', confidence_threshold=0.5)

# Detect faces in an image
image_path = "uploads/20260412_121708_39d4226d.jpg"
faces = detector.detect_faces(image_path)

print(f"Found {len(faces)} face(s)")
for i, face in enumerate(faces):
    x, y, w, h = face['bounding_box']
    confidence = face['confidence']
    print(f"Face {i+1}: position=({x}, {y}, {w}, {h}), confidence={confidence:.2%}")


# ========================================
# EXAMPLE 2: High Accuracy Detection
# ========================================

# Use medium model for better accuracy (slower but more precise)
high_accuracy_detector = YOLOFaceDetector(
    model_size='m',              # Medium model
    confidence_threshold=0.4     # Lower threshold to catch more faces
)

faces = high_accuracy_detector.detect_faces(image_path)
print(f"\nHigh accuracy detection: {len(faces)} face(s) found")


# ========================================
# EXAMPLE 3: Using AdvancedFaceDetector (Recommended)
# ========================================
from ai.advanced_face_detection import AdvancedFaceDetector

# YOLO is now the default engine
detector = AdvancedFaceDetector(engine='yolov8')
faces = detector.detect_faces(image_path)

print(f"\nAdvancedFaceDetector with YOLO: {len(faces)} face(s)")


# ========================================
# EXAMPLE 4: Auto-Detection (Tries Best Engine)
# ========================================
detector = AdvancedFaceDetector(engine='yolov8')
faces = detector.detect_faces_auto(image_path)

print(f"\nAuto-detection: {len(faces)} face(s)")


# ========================================
# EXAMPLE 5: Crop and Save Detected Faces
# ========================================
output_folder = "uploads/cropped_faces"
cropped_paths = detector.crop_and_save_faces(image_path, output_folder)

print(f"\nCropped and saved {len(cropped_paths)} face(s):")
for path in cropped_paths:
    print(f"  - {path}")


# ========================================
# EXAMPLE 6: Batch Processing Multiple Images
# ========================================
import os

# Get all images from a folder
dataset_path = "dataset/missing_persons"
image_files = [
    os.path.join(dataset_path, f)
    for f in os.listdir(dataset_path)
    if f.endswith(('.jpg', '.jpeg', '.png'))
]

# Process all images
detector = YOLOFaceDetector(model_size='n')
results = detector.detect_faces_batch(image_files)

print(f"\nBatch processing results:")
for img_path, faces in results.items():
    filename = os.path.basename(img_path)
    print(f"  {filename}: {len(faces)} face(s)")


# ========================================
# EXAMPLE 7: Visualization - Draw Detections
# ========================================
output_image = "uploads/yolo_detected.jpg"
success = detector.draw_detections(image_path, output_image)

if success:
    print(f"\nDetection visualization saved to: {output_image}")


# ========================================
# EXAMPLE 8: API Usage (via HTTP requests)
# ========================================
import requests

# Detect faces via API
url = "http://127.0.0.1:8000/api/face/detect-face"

with open(image_path, "rb") as f:
    files = {"file": f}
    data = {
        "engine": "yolov8",        # Use YOLO engine
        "crop_faces": "true"       # Crop detected faces
    }
    
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    print(f"\nAPI Response:")
    print(f"Status: {result['status']}")
    print(f"Total faces: {result['total_faces']}")
    
    for face in result.get('faces', []):
        print(f"  Face #{face['face_index']}: confidence={face['confidence']:.2%}")


# ========================================
# EXAMPLE 9: Compare All Detection Engines
# ========================================
engines = ['yolov8', 'retinaface', 'mtcnn', 'mediapipe', 'opencv']

print("\n" + "="*60)
print("ENGINE COMPARISON")
print("="*60)

for engine in engines:
    try:
        detector = AdvancedFaceDetector(engine=engine)
        faces = detector.detect_faces(image_path)
        print(f"{engine:15} -> {len(faces)} face(s)")
    except Exception as e:
        print(f"{engine:15} -> Error: {e}")


# ========================================
# EXAMPLE 10: Integration with Missing Person Matching
# ========================================
from ai.advanced_face_recognition import AdvancedFaceRecognition

# Step 1: Detect faces with YOLO
detector = AdvancedFaceDetector(engine='yolov8')
faces = detector.detect_faces(image_path)

if faces:
    print(f"\nFound {len(faces)} face(s) to match against database")
    
    # Step 2: For each detected face, try to recognize
    recognizer = AdvancedFaceRecognition(model='hog')
    
    for i, face in enumerate(faces):
        x, y, w, h = face['bounding_box']
        print(f"\nProcessing face {i+1}...")
        
        # The recognition system will automatically use the detected face
        # This is where you'd integrate with your matching pipeline
        print(f"  Face location: ({x}, {y}, {w}, {h})")
        print(f"  Ready for recognition/matching...")


# ========================================
# TIPS FOR BEST RESULTS
# ========================================
"""
TIP 1: Model Selection
- Use 'n' (nano) for real-time/video processing
- Use 's' (small) for general purpose
- Use 'm' (medium) or 'l' (large) for critical matching

TIP 2: Confidence Threshold
- 0.5 (default): Good balance
- 0.3-0.4: Detect more faces, but may have false positives
- 0.6-0.7: Fewer false positives, but might miss some faces

TIP 3: Speed vs Accuracy
- Fastest: YOLOv8-N + confidence 0.6
- Balanced: YOLOv8-S + confidence 0.5
- Most Accurate: YOLOv8-M/L + confidence 0.3

TIP 4: Batch Processing
- Process multiple images at once for efficiency
- Use detect_faces_batch() method

TIP 5: Fallback Strategy
- Try YOLO first
- If no faces detected, try RetinaFace
- If still no faces, use OpenCV as last resort
"""
