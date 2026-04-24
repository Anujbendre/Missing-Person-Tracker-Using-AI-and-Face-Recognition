import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { timeout, catchError } from 'rxjs/operators';
import { throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl = 'http://127.0.0.1:8000';
  private apiTimeout = 5000; // 5 seconds timeout

  constructor(private http: HttpClient) {}

  // ================= POLICE AUTH =================
  policeSignup(data: any): Observable<any> {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('email', data.email);
    formData.append('password', data.password);
    formData.append('mobile', data.mobile);
    formData.append('station_name', data.station_name);
    return this.http.post(`${this.baseUrl}/police/signup`, formData);
  }

  policeLogin(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/police/login`, data);
  }

  // Alias methods for compatibility
  login(data: any): Observable<any> {
    return this.policeLogin(data);
  }

  register(data: any): Observable<any> {
    return this.policeSignup(data);
  }

  getStations(): Observable<any> {
    return this.http.get(`${this.baseUrl}/stations`);
  }

  // ================= MISSING PERSON =================
  reportMissing(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/missing`, data);
  }

  getAllCases(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/all-cases`).pipe(
      timeout(this.apiTimeout),
      catchError(this.handleError)
    );
  }

  getSingleCase(caseId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/case/${caseId}`).pipe(
      timeout(this.apiTimeout),
      catchError(this.handleError)
    );
  }

  getPoliceCases(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/all-cases`);
  }

  updateCaseStatus(caseId: number, status: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/api/update-case/${caseId}`, { status });
  }

  // ================= OTP =================
  sendOTP(mobile: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/send-otp`, { mobile });
  }

  verifyOTP(mobile: string, otp: number): Observable<any> {
    return this.http.post(`${this.baseUrl}/verify-otp`, { mobile, otp });
  }

  // ================= FIR =================
  applyFIR(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/fir`, data);
  }

  getFIRs(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/fir`);
  }

  // ================= CCTV / FRAMES =================
  saveFrame(imageBase64: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/save-frame`, { image: imageBase64 });
  }

  getFrames(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/frames`);
  }

  // ================= FACE RECOGNITION =================
  detectImage(imagePath: string, selectedPersonId?: number): Observable<any> {
    const payload: any = { image_path: imagePath };
    if (selectedPersonId) {
      payload.selected_person_id = selectedPersonId;
    }
    return this.http.post(`${this.baseUrl}/detect-image`, payload);
  }

  autoDetect(): Observable<any> {
    return this.http.get(`${this.baseUrl}/auto-detect`);
  }

  // Advanced face recognition with CNN embeddings
  recognizeFace(imageFile: File): Observable<any> {
    const formData = new FormData();
    formData.append('image', imageFile);
    return this.http.post(`${this.baseUrl}/recognize`, formData);
  }

  encodeDataset(): Observable<any> {
    return this.http.post(`${this.baseUrl}/encode-dataset`, {});
  }

  // ================= IMAGE URL HELPER =================
  getImageUrl(filename: string): string {
    if (!filename) return '';
    
    // Check if filename is a full URL or path
    if (filename.startsWith('http://') || filename.startsWith('https://')) {
      return filename;
    }
    
    // Handle CCTV images with uploads/cctv/ prefix
    if (filename.startsWith('uploads/cctv/')) {
      const cleanFilename = filename.replace('uploads/cctv/', '');
      const url = `${this.baseUrl}/cctv/${cleanFilename}`;
      console.log('📹 CCTV Image URL:', url);
      return url;
    }
    
    // Handle CCTV images with cctv/ prefix (legacy)
    if (filename.startsWith('cctv/')) {
      return `${this.baseUrl}/cctv/${filename.replace('cctv/', '')}`;
    }
    
    // If filename already starts with /uploads/, use it as-is
    if (filename.startsWith('/uploads/')) {
      return `${this.baseUrl}${filename}`;
    }
    
    // If filename starts with uploads/, add leading slash
    if (filename.startsWith('uploads/')) {
      return `${this.baseUrl}/${filename}`;
    }
    
    // Otherwise, assume it's just a filename and construct the URL
    // Default to uploads folder for missing person photos
    return `${this.baseUrl}/uploads/${filename}`;
  }

  // ================= FEATURE 2: ALERTS =================
  getAlerts(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/alerts`);
  }

  markAlertRead(alertId: number): Observable<any> {
    return this.http.put(`${this.baseUrl}/api/alert/${alertId}/read`, {});
  }

  logAlert(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/log-alert`, data);
  }

  // ================= FEATURE 3: CASE HISTORY =================
  getCaseHistory(caseId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/case-history/${caseId}`);
  }

  // ================= FEATURE 4: CAMERA MANAGEMENT =================
  addCamera(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/add-camera`, data);
  }

  getCameras(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/cameras`);
  }

  updateCamera(id: number, data: any): Observable<any> {
    return this.http.put(`${this.baseUrl}/api/camera/${id}`, data);
  }

  deleteCamera(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/api/camera/${id}`);
  }

  // ================= FEATURE 5: VIDEO DETECTION =================
  detectVideo(formData: FormData): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/detect-video`, formData);
  }

  // ================= FEATURE 6: MULTI-FACE DETECTION =================
  detectMultipleFaces(formData: FormData): Observable<any> {
    return this.http.post(`${this.baseUrl}/api/detect-faces`, formData);
  }

  // ================= FEATURE 8: ANALYTICS =================
  getAnalytics(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/analytics`).pipe(
      timeout(this.apiTimeout),
      catchError(this.handleError)
    );
  }

  // ================= FEATURE 9: DETECTION LOGS =================
  getDetectionLogs(): Observable<any> {
    return this.http.get(`${this.baseUrl}/api/detection-logs`).pipe(
      timeout(this.apiTimeout),
      catchError(this.handleError)
    );
  }

  // ================= FEATURE 10: CITIZEN AUTH =================
  citizenSignup(data: any): Observable<any> {
    const formData = new FormData();
    formData.append('name', data.name);
    formData.append('email', data.email);
    formData.append('password', data.password);
    formData.append('mobile', data.mobile);
    return this.http.post(`${this.baseUrl}/citizen/signup`, formData);
  }

  // ================= ERROR HANDLER =================
  private handleError(error: any) {
    console.error('API Error:', error);
    let errorMessage = 'An error occurred';
    
    if (error.name === 'TimeoutError') {
      errorMessage = 'Request timeout. Please check your connection.';
    } else if (error.status === 0) {
      errorMessage = 'Cannot connect to server. Please ensure backend is running.';
    } else if (error.status === 404) {
      errorMessage = 'API endpoint not found.';
    } else if (error.status === 500) {
      errorMessage = 'Server error. Please try again later.';
    }
    
    return throwError(() => new Error(errorMessage));
  }
}