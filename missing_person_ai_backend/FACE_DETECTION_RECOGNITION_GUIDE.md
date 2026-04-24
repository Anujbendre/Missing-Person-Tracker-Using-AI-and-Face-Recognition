# Advanced Face Detection & Recognition System

## 🎯 Overview

This system provides advanced face detection and recognition capabilities for the Missing Person Tracking System using state-of-the-art AI libraries:

- **RetinaFace**: Most accurate face detection
- **MTCNN**: Multi-task Cascaded Convolutional Networks for face detection
- **MediaPipe**: Real-time face detection (fastest)
- **DeepFace**: Face recognition and attribute analysis

## 📦 Installation

### 1. Install Dependencies

```bash
cd missing_person_ai_backend
pip install -r requirements.txt
```

### 2. Required Libraries

The system uses the following key libraries:

- `mediapipe==0.10.8` - Real-time face detection
- `deepface==0.0.79` - Face recognition and analysis
- `retina-face==0.0.14` - High-accuracy face detection
- `mtcnn==0.1.1` - Multi-task face detection
- `opencv-python==4.8.1.78` - Image processing
- `tensorflow==2.15.0` - Deep learning backend
- `numpy==1.24.3` - Numerical operations

## 🚀 API Endpoints

All face-related endpoints are prefixed with `/api/face`

### 1. Face Detection

**Endpoint**: `POST /api/face/detect-face`

Detect faces in uploaded image using multiple engines.

**Parameters:**
- `file`: Image file (required)
- `engine`: Detection engine - `retinaface`, `mtcnn`, or `mediapipe` (default: `retinaface`)
- `crop_faces`: Whether to crop detected faces (default: `true`)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/face/detect-face" \
  -F "file=@person.jpg" \
  -F "engine=retinaface" \
  -F "crop_faces=true"
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Detected 1 face(s)",
  "total_faces": 1,
  "faces": [
    {
      "face_index": 0,
      "bounding_box": {
        "x": 150,
        "y": 120,
        "width": 200,
        "height": 240
      },
      "confidence": 0.9876,
      "engine": "retinaface",
      "cropped_face_path": "uploads/cropped_faces/person_face_0.jpg"
    }
  ],
  "image_path": "/uploads/face_uploads/20260413_143022_abc123.jpg"
}
```

### 2. Face Recognition

**Endpoint**: `POST /api/face/recognize-face`

Recognize face by comparing with database.

**Parameters:**
- `file`: Image file (required)
- `model_name`: Recognition model - `VGG-Face`, `Facenet`, `OpenFace`, `ArcFace` (default: `VGG-Face`)
- `threshold`: Match threshold 0-100 (default: `70`)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/face/recognize-face" \
  -F "file=@unknown_person.jpg" \
  -F "model_name=VGG-Face" \
  -F "threshold=70"
```

**Example Response (Match Found):**
```json
{
  "status": "success",
  "match_found": true,
  "person_id": "person_101",
  "name": "Person 101",
  "match_percentage": 85.42,
  "confidence": 85.42,
  "all_matches": [
    {
      "person_id": "person_101",
      "name": "Person 101",
      "match_percentage": 85.42,
      "image_path": "dataset/missing_persons/person_101.jpg"
    }
  ],
  "image_path": "/uploads/face_uploads/20260413_143022_def456.jpg"
}
```

**Example Response (No Match):**
```json
{
  "status": "success",
  "match_found": false,
  "message": "No match found in database",
  "image_path": "/uploads/face_uploads/20260413_143022_def456.jpg"
}
```

### 3. Face Verification

**Endpoint**: `POST /api/face/verify-faces`

Verify if two faces belong to the same person.

**Parameters:**
- `file1`: First image file (required)
- `file2`: Second image file (required)
- `model_name`: Recognition model (default: `VGG-Face`)

**Example Response:**
```json
{
  "status": "success",
  "verified": true,
  "match_percentage": 92.5,
  "distance": 0.35,
  "threshold": 0.6
}
```

### 4. Face Attribute Analysis

**Endpoint**: `POST /api/face/analyze-face`

Analyze face attributes (age, gender, emotion, race).

**Parameters:**
- `file`: Image file (required)
- `analyze_attributes`: Whether to analyze (default: `true`)

**Example Response:**
```json
{
  "status": "success",
  "attributes": {
    "age": 28,
    "gender": "Man",
    "emotion": "neutral",
    "race": "white",
    "emotion_scores": {
      "happy": 0.15,
      "sad": 0.05,
      "angry": 0.02,
      "fear": 0.01,
      "disgust": 0.01,
      "neutral": 0.76
    }
  },
  "image_path": "/uploads/face_uploads/20260413_143022_ghi789.jpg"
}
```

### 5. MediaPipe Detection

**Endpoint**: `POST /api/face/mediapipe-detect`

Detect faces using MediaPipe (optimized for speed).

**Parameters:**
- `file`: Image file (required)
- `return_annotated`: Return annotated image (default: `true`)

### 6. Webcam Stream

**Endpoint**: `GET /api/face/webcam-stream?camera_id=0`

Stream webcam feed with real-time face detection.

**Usage in Browser:**
```
http://localhost:8000/api/face/webcam-stream?camera_id=0
```

### 7. Load Face Database

**Endpoint**: `POST /api/face/load-database`

Load face images from database folder for recognition.

**Parameters:**
- `database_path`: Path to folder with face images (default: `dataset/missing_persons`)
- `model_name`: Recognition model (default: `VGG-Face`)

### 8. Get Supported Models

**Endpoint**: `GET /api/face/supported-models`

Get list of all supported detection engines and recognition models.

**Example Response:**
```json
{
  "detection_engines": ["retinaface", "mtcnn", "mediapipe"],
  "recognition_models": ["VGG-Face", "Facenet", "OpenFace", "ArcFace", "DeepID"],
  "analysis_attributes": ["age", "gender", "emotion", "race"]
}
```

## 🗂️ Folder Structure

```
missing_person_ai_backend/
├── ai/
│   ├── advanced_face_detection.py    # RetinaFace, MTCNN, MediaPipe detection
│   ├── deepface_recognition.py       # DeepFace recognition service
│   ├── mediapipe_detection.py        # MediaPipe real-time detection
│   └── face_api_routes.py            # API endpoints
├── uploads/
│   ├── face_uploads/                 # Uploaded images
│   └── cropped_faces/                # Cropped face images
├── dataset/
│   └── missing_persons/              # Database of known faces
└── app.py                            # Main FastAPI application
```

## 🎯 Usage Examples

### Python Example - Face Detection

```python
import requests

# Detect faces
url = "http://localhost:8000/api/face/detect-face"
files = {"file": open("test_image.jpg", "rb")}
data = {"engine": "retinaface", "crop_faces": "true"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Python Example - Face Recognition

```python
import requests

# Recognize face
url = "http://localhost:8000/api/face/recognize-face"
files = {"file": open("unknown_person.jpg", "rb")}
data = {"model_name": "VGG-Face", "threshold": "70"}

response = requests.post(url, files=files, data=data)
result = response.json()

if result["match_found"]:
    print(f"Match found: {result['name']} ({result['match_percentage']}%)")
else:
    print("No match found")
```

### Angular/JavaScript Example

```typescript
// Face Detection
async detectFace(imageFile: File) {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('engine', 'retinaface');
  formData.append('crop_faces', 'true');

  const response = await fetch('http://localhost:8000/api/face/detect-face', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  console.log('Detected faces:', result.total_faces);
  return result;
}

// Face Recognition
async recognizeFace(imageFile: File) {
  const formData = new FormData();
  formData.append('file', imageFile);
  formData.append('model_name', 'VGG-Face');
  formData.append('threshold', '70');

  const response = await fetch('http://localhost:8000/api/face/recognize-face', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  
  if (result.match_found) {
    console.log(`Match: ${result.name} (${result.match_percentage}%)`);
  } else {
    console.log('No match found');
  }
  
  return result;
}
```

## ⚙️ Configuration

### Detection Engines Comparison

| Engine | Accuracy | Speed | Best Use Case |
|--------|----------|-------|---------------|
| RetinaFace | ⭐⭐⭐⭐⭐ | Medium | Production, high accuracy |
| MTCNN | ⭐⭐⭐⭐ | Medium | Good balance |
| MediaPipe | ⭐⭐⭐ | Fast | Real-time, webcam |

### Recognition Models Comparison

| Model | Accuracy | Speed | Embedding Size |
|-------|----------|-------|----------------|
| VGG-Face | ⭐⭐⭐⭐ | Fast | 2622-d |
| Facenet | ⭐⭐⭐⭐⭐ | Medium | 128-d |
| OpenFace | ⭐⭐⭐ | Fast | 128-d |
| ArcFace | ⭐⭐⭐⭐⭐ | Medium | 512-d |

## 🔧 Troubleshooting

### Issue: No faces detected
- Ensure image has clear, front-facing faces
- Try different detection engine (retinaface is most accurate)
- Check image quality and lighting

### Issue: No matches found
- Add face images to `dataset/missing_persons/` folder
- Format: `person_101.jpg`, `person_102.jpg`, etc.
- Run `/api/face/load-database` endpoint to load faces
- Lower the threshold parameter (try 60 or 65)

### Issue: Slow performance
- Use MediaPipe for faster detection
- Use VGG-Face model for faster recognition
- Resize images before uploading (max 1920x1080)

### Issue: TensorFlow errors
- Ensure TensorFlow 2.15.0 is installed
- Check CUDA compatibility if using GPU
- Try CPU-only mode if GPU issues persist

## 📊 Performance Optimization

### Image Preprocessing
The system automatically handles:
- Image resizing for optimal processing
- Format conversion (JPG, PNG, BMP)
- Quality optimization

### Best Practices
1. **Use appropriate engine**: RetinaFace for accuracy, MediaPipe for speed
2. **Set proper threshold**: 70-80% for most use cases
3. **Pre-load database**: Call `/load-database` on startup
4. **Cache encodings**: System automatically saves/loads encodings
5. **Batch processing**: Use `/detect-multiple` for multiple images

## 🔐 Security Considerations

- File type validation (only images allowed)
- Unique filename generation to prevent conflicts
- Automatic file cleanup recommended
- CORS enabled for Angular frontend integration

## 📝 Next Steps

1. Add more face images to `dataset/missing_persons/`
2. Test all endpoints with sample images
3. Integrate with Angular frontend
4. Configure database connection for storing recognition results
5. Set up automatic face encoding on new person registration

## 🤝 Support

For issues or questions:
- Check the logs for detailed error messages
- Ensure all dependencies are installed
- Verify image formats and paths
- Test with sample images first

## 🎓 Additional Resources

- [DeepFace Documentation](https://github.com/serengil/deepface)
- [MediaPipe Face Detection](https://google.github.io/mediapipe/solutions/face_detection)
- [RetinaFace Paper](https://arxiv.org/abs/1905.00641)
- [MTCNN Paper](https://arxiv.org/abs/1604.02878)
