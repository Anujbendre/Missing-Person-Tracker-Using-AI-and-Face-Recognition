# Quick Start Guide - Advanced Face Detection & Recognition

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd missing_person_ai_backend
pip install -r requirements.txt
```

**Note**: First installation may take 5-10 minutes as TensorFlow and other libraries are large.

### Step 2: Test the System

```bash
python test_face_system.py
```

This will verify all components are working correctly.

### Step 3: Start the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test API Endpoints

Open your browser or use Postman to test:

1. **Face Detection**: `POST http://localhost:8000/api/face/detect-face`
2. **Face Recognition**: `POST http://localhost:8000/api/face/recognize-face`
3. **Face Analysis**: `POST http://localhost:8000/api/face/analyze-face`
4. **API Documentation**: `http://localhost:8000/docs` (Swagger UI)

## 📋 Quick API Examples

### Example 1: Detect Faces

```bash
curl -X POST "http://localhost:8000/api/face/detect-face" \
  -F "file=@your_image.jpg" \
  -F "engine=retinaface" \
  -F "crop_faces=true"
```

### Example 2: Recognize Face

```bash
curl -X POST "http://localhost:8000/api/face/recognize-face" \
  -F "file=@unknown_person.jpg" \
  -F "model_name=VGG-Face" \
  -F "threshold=70"
```

### Example 3: Analyze Face Attributes

```bash
curl -X POST "http://localhost:8000/api/face/analyze-face" \
  -F "file=@person.jpg"
```

## 🎯 Using with Angular Frontend

### Service File (face.service.ts)

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FaceService {
  private baseUrl = 'http://localhost:8000/api/face';

  constructor(private http: HttpClient) { }

  // Detect faces in image
  detectFace(file: File, engine: string = 'retinaface'): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('engine', engine);
    formData.append('crop_faces', 'true');
    
    return this.http.post(`${this.baseUrl}/detect-face`, formData);
  }

  // Recognize face
  recognizeFace(file: File, threshold: number = 70): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_name', 'VGG-Face');
    formData.append('threshold', threshold.toString());
    
    return this.http.post(`${this.baseUrl}/recognize-face`, formData);
  }

  // Analyze face attributes
  analyzeFace(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post(`${this.baseUrl}/analyze-face`, formData);
  }
}
```

### Component Usage

```typescript
import { Component } from '@angular/core';
import { FaceService } from './face.service';

@Component({
  selector: 'app-face-detection',
  template: `
    <input type="file" (change)="onFileSelected($event)" accept="image/*">
    <button (click)="detectFaces()">Detect Faces</button>
    <button (click)="recognizeFace()">Recognize Face</button>
    
    <div *ngIf="result">
      <h3>Result:</h3>
      <pre>{{ result | json }}</pre>
    </div>
  `
})
export class FaceDetectionComponent {
  selectedFile: File | null = null;
  result: any = null;

  constructor(private faceService: FaceService) {}

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  detectFaces() {
    if (this.selectedFile) {
      this.faceService.detectFace(this.selectedFile).subscribe({
        next: (data) => {
          this.result = data;
          console.log('Faces detected:', data.total_faces);
        },
        error: (error) => console.error('Error:', error)
      });
    }
  }

  recognizeFace() {
    if (this.selectedFile) {
      this.faceService.recognizeFace(this.selectedFile).subscribe({
        next: (data) => {
          this.result = data;
          if (data.match_found) {
            console.log(`Match: ${data.name} (${data.match_percentage}%)`);
          } else {
            console.log('No match found');
          }
        },
        error: (error) => console.error('Error:', error)
      });
    }
  }
}
```

## 📁 Prepare Your Database

Add face images to `dataset/missing_persons/` folder:

```
dataset/
└── missing_persons/
    ├── person_101.jpg
    ├── person_102.jpg
    ├── person_103.jpg
    └── ...
```

Then load the database:

```bash
curl -X POST "http://localhost:8000/api/face/load-database" \
  -F "database_path=dataset/missing_persons" \
  -F "model_name=VGG-Face"
```

## 🔍 Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/face/detect-face` | POST | Detect faces in image |
| `/api/face/recognize-face` | POST | Recognize face from database |
| `/api/face/verify-faces` | POST | Verify if two faces match |
| `/api/face/analyze-face` | POST | Analyze face attributes |
| `/api/face/mediapipe-detect` | POST | Detect with MediaPipe |
| `/api/face/webcam-stream` | GET | Webcam stream with detection |
| `/api/face/load-database` | POST | Load face database |
| `/api/face/supported-models` | GET | List supported models |

## ⚡ Performance Tips

1. **For fastest detection**: Use `engine=mediapipe`
2. **For best accuracy**: Use `engine=retinaface`
3. **For recognition**: Use `model_name=Facenet` (most accurate)
4. **Lower threshold** (60-65) if no matches found
5. **Higher threshold** (75-80) for stricter matching

## 🐛 Common Issues

### Issue: "No module named 'xyz'"
```bash
pip install xyz
```

### Issue: "No faces detected"
- Try different engine: `engine=retinaface`
- Ensure image has clear, front-facing face
- Check image quality and lighting

### Issue: "No match found"
- Add images to `dataset/missing_persons/`
- Run `/api/face/load-database`
- Lower threshold to 60

### Issue: Slow performance
- Use MediaPipe for detection
- Use VGG-Face for recognition
- Resize images to max 1920x1080

## 📚 Full Documentation

See `FACE_DETECTION_RECOGNITION_GUIDE.md` for complete documentation.

## 🎉 You're Ready!

The system is now ready to use. Start the server and begin testing!

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for interactive API documentation.
