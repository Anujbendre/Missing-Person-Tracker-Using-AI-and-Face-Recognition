// Angular Service for Face Detection and Recognition API
// Add this to your Angular project: src/app/services/face.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FaceDetectionResult {
  status: string;
  message: string;
  total_faces: number;
  faces: Array<{
    face_index: number;
    bounding_box: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    confidence: number;
    engine: string;
    cropped_face_path?: string;
  }>;
  image_path: string;
  annotated_image_path?: string;
}

export interface FaceRecognitionResult {
  status: string;
  match_found: boolean;
  person_id?: string;
  name?: string;
  match_percentage?: number;
  confidence?: number;
  message?: string;
  all_matches?: Array<{
    person_id: string;
    name: string;
    match_percentage: number;
    image_path: string;
  }>;
  image_path: string;
}

export interface FaceAnalysisResult {
  status: string;
  attributes: {
    age: number | string;
    gender: string;
    emotion: string;
    race: string;
    emotion_scores?: any;
    race_scores?: any;
  };
  image_path: string;
}

@Injectable({
  providedIn: 'root'
})
export class FaceService {
  // Update this URL to match your backend
  private apiUrl = 'http://localhost:8000/api/face';

  constructor(private http: HttpClient) { }

  /**
   * Detect faces in an image
   * @param file Image file
   * @param engine Detection engine (retinaface, mtcnn, mediapipe)
   * @param cropFaces Whether to crop detected faces
   */
  detectFace(
    file: File, 
    engine: string = 'retinaface', 
    cropFaces: boolean = true
  ): Observable<FaceDetectionResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('engine', engine);
    formData.append('crop_faces', cropFaces.toString());

    return this.http.post<FaceDetectionResult>(
      `${this.apiUrl}/detect-face`, 
      formData
    );
  }

  /**
   * Recognize face by comparing with database
   * @param file Image file with face
   * @param modelName Recognition model (VGG-Face, Facenet, OpenFace, ArcFace)
   * @param threshold Match threshold (0-100)
   */
  recognizeFace(
    file: File, 
    modelName: string = 'VGG-Face', 
    threshold: number = 70
  ): Observable<FaceRecognitionResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_name', modelName);
    formData.append('threshold', threshold.toString());

    return this.http.post<FaceRecognitionResult>(
      `${this.apiUrl}/recognize-face`, 
      formData
    );
  }

  /**
   * Verify if two faces belong to the same person
   * @param file1 First image file
   * @param file2 Second image file
   * @param modelName Recognition model
   */
  verifyFaces(
    file1: File, 
    file2: File, 
    modelName: string = 'VGG-Face'
  ): Observable<any> {
    const formData = new FormData();
    formData.append('file1', file1);
    formData.append('file2', file2);
    formData.append('model_name', modelName);

    return this.http.post<any>(
      `${this.apiUrl}/verify-faces`, 
      formData
    );
  }

  /**
   * Analyze face attributes (age, gender, emotion, race)
   * @param file Image file
   */
  analyzeFace(file: File): Observable<FaceAnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('analyze_attributes', 'true');

    return this.http.post<FaceAnalysisResult>(
      `${this.apiUrl}/analyze-face`, 
      formData
    );
  }

  /**
   * Detect faces using MediaPipe
   * @param file Image file
   * @param returnAnnotated Whether to return annotated image
   */
  detectWithMediaPipe(
    file: File, 
    returnAnnotated: boolean = true
  ): Observable<FaceDetectionResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('return_annotated', returnAnnotated.toString());

    return this.http.post<FaceDetectionResult>(
      `${this.apiUrl}/mediapipe-detect`, 
      formData
    );
  }

  /**
   * Load face database for recognition
   * @param databasePath Path to folder with face images
   * @param modelName Recognition model
   */
  loadDatabase(
    databasePath: string = 'dataset/missing_persons', 
    modelName: string = 'VGG-Face'
  ): Observable<any> {
    const formData = new FormData();
    formData.append('database_path', databasePath);
    formData.append('model_name', modelName);

    return this.http.post<any>(
      `${this.apiUrl}/load-database`, 
      formData
    );
  }

  /**
   * Get supported models and engines
   */
  getSupportedModels(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/supported-models`);
  }

  /**
   * Get webcam stream URL
   * @param cameraId Camera device ID
   */
  getWebcamStreamUrl(cameraId: number = 0): string {
    return `${this.apiUrl}/webcam-stream?camera_id=${cameraId}`;
  }

  /**
   * Helper method to convert File to base64
   * @param file Image file
   */
  fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  }

  /**
   * Helper method to draw face bounding boxes on canvas
   * @param canvas HTML Canvas element
   * @param image Image element
   * @param faces Array of face detection results
   */
  drawFaceBoxes(
    canvas: HTMLCanvasElement, 
    image: HTMLImageElement, 
    faces: FaceDetectionResult['faces']
  ): void {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas dimensions
    canvas.width = image.width;
    canvas.height = image.height;

    // Draw image
    ctx.drawImage(image, 0, 0);

    // Draw face boxes
    faces.forEach((face, index) => {
      const { x, y, width, height } = face.bounding_box;

      // Draw rectangle
      ctx.strokeStyle = '#00FF00';
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, width, height);

      // Draw label background
      const label = `Face ${index + 1}: ${(face.confidence * 100).toFixed(1)}%`;
      ctx.font = 'bold 16px Arial';
      const textMetrics = ctx.measureText(label);
      const textHeight = 20;
      
      ctx.fillStyle = 'rgba(0, 255, 0, 0.7)';
      ctx.fillRect(x, y - textHeight, textMetrics.width + 10, textHeight);

      // Draw label text
      ctx.fillStyle = '#000000';
      ctx.fillText(label, x + 5, y - 5);
    });
  }
}
