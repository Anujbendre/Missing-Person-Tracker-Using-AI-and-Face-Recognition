import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { AlertService } from '../../services/alert.service';

@Component({
  selector: 'app-ai-recognition',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './ai-recognition.html',
  styleUrls: ['./ai-recognition.css']
})
export class AiRecognitionComponent implements OnInit {

  // Data arrays
  cctvImages: any[] = [];
  missingPersons: any[] = [];
  
  // Selected items
  selectedCase: any = null;
  selectedCCTVImage: any = null;
  
  // Scanning state
  isScanning: boolean = false;
  scanProgress: number = 0;
  scanStatus: string = '';
  scanAbortController: AbortController | null = null; // For cancelling HTTP requests
  
  // Results
  scanResult: any = null;
  scanHistory: any[] = [];
  
  // UI State
  activeTab: 'cctv' | 'cases' = 'cases';
  showResults: boolean = false;
  
  // Image Preview
  showImagePreview: boolean = false;
  previewImageUrl: string = '';
  previewImageType: '' | 'cctv' | 'person' = '';
  
  // Active Alerts
  activeAlerts: any[] = [];
  showAlertPanel: boolean = false;

  // Advanced Recognition
  selectedImageFile: File | null = null;
  advancedRecognitionResult: any = null;
  showAdvancedRecognition: boolean = false;

  // Statistics for circular graph
  totalScans: number = 0;
  matchesFound: number = 0;
  notFound: number = 0;
  matchPercentage: number = 0;
  notFoundPercentage: number = 0;

  constructor(
    private authService: AuthService,
    private alertService: AlertService,
    private cdr: ChangeDetectorRef // Add change detector
  ) {}

  ngOnInit() {
    // Request notification permission for match alerts
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
    
    // Load data in parallel for faster loading
    this.loadCCTVImages();
    this.loadMissingPersons();
  }

  // ================= LOAD CCTV IMAGES =================
  loadCCTVImages() {
    this.authService.getFrames().subscribe({
      next: (res: any) => {
        console.log('📹 CCTV Images loaded:', res);
        this.cctvImages = res?.data || [];
        if (this.cctvImages.length === 0) {
          console.warn('⚠️ No CCTV images found in database');
        }
      },
      error: (err) => {
        console.error('❌ Error loading CCTV images:', err);
      }
    });
  }

  // ================= LOAD MISSING PERSONS =================
  loadMissingPersons() {
    this.authService.getAllCases().subscribe({
      next: (res: any) => {
        console.log('👤 Missing Persons loaded:', res);
        this.missingPersons = res?.data || [];
      },
      error: (err) => {
        console.error('❌ Error loading missing persons:', err);
        alert('Failed to load missing persons data');
      }
    });
  }

  // ================= SELECT CASE =================
  selectCase(person: any) {
    this.selectedCase = person;
    this.scanResult = null;
    this.showResults = false;
    console.log('✅ Selected case:', person.full_name);
  }

  // ================= SELECT CCTV IMAGE =================
  selectCCTVImage(image: any) {
    this.selectedCCTVImage = image;
    this.scanResult = null;
    this.showResults = false;
    console.log('✅ Selected CCTV image:', image.image_path);
  }

  // ================= SCAN SINGLE IMAGE =================
  scanImage() {
    if (!this.selectedCase) {
      alert('⚠️ Please select a missing person case first');
      return;
    }

    if (!this.selectedCCTVImage) {
      alert('⚠️ Please select a CCTV image to scan');
      return;
    }

    // Clear previous results
    this.scanResult = null;
    this.showResults = false;
    
    // Start scanning selected image only
    this.startScanning(this.selectedCCTVImage.image_path);
  }

  // ================= SCAN ALL CCTV IMAGES =================
  scanAllImages() {
    if (!this.selectedCase) {
      alert('⚠️ Please select a missing person case first');
      return;
    }

    if (this.cctvImages.length === 0) {
      alert('⚠️ No CCTV images available in database');
      return;
    }

    this.startScanningAll();
  }

  // ================= START SCANNING (Single) =================
  private startScanning(imagePath: string) {
    this.isScanning = true;
    this.scanProgress = 0;
    this.scanStatus = 'Initializing face detection...';
    this.showResults = false;
    this.scanAbortController = new AbortController();

    // Call backend API directly (no animation delay for speed)
    console.log('👤 Selected Person ID:', this.selectedCase?.person_id);
    this.authService.detectImage(imagePath, this.selectedCase?.person_id).subscribe({
      next: (result: any) => {
        console.log('🔍 Scan result:', result);
        console.log('📊 Result status:', result.status);
        
        this.isScanning = false;
        this.scanAbortController = null;
        this.scanProgress = 100;
        
        // Process result IMMEDIATELY for fast response
        if (result.status === 'MATCH FOUND') {
          console.log('✅ MATCH FOUND!', result.name, result.confidence);
          
          this.scanResult = {
            type: 'match',
            confidence: result.confidence,
            name: result.name,
            personId: result.person_id,
            photo: result.photo,
            scannedImage: imagePath,
            timestamp: new Date().toLocaleString()
          };
          
          this.scanStatus = 'Match found!';
          this.showResults = true;
          
          // 🎯 SHOW POPUP ALERT IMMEDIATELY
          const alert = this.alertService.showMatchAlert(
            result.name,
            result.confidence,
            result.person_id,
            result.photo
          );
          this.activeAlerts.unshift(alert);
          this.showAlertPanel = true;
          
          // Show browser notification for instant alert
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('🎯 Match Found!', {
              body: `${result.name} - ${result.confidence}% match`,
              icon: '/assets/icon.png'
            });
          }
          
          // Auto-hide alert after 15 seconds
          setTimeout(() => {
            this.showAlertPanel = false;
          }, 15000);
          
        } else if (result.status === 'NOT FOUND') {
          console.log('❌ NO MATCH FOUND');
          
          this.scanResult = {
            type: 'no-match',
            message: `No match found for ${this.selectedCase?.full_name || 'selected person'} in this image`,
            scannedImage: imagePath,
            timestamp: new Date().toLocaleString()
          };
          
          this.scanStatus = 'No match found';
          this.showResults = true;
          
        } else if (result.status === 'No face detected') {
          console.log('⚠️ NO FACE DETECTED');
          
          this.scanResult = {
            type: 'error',
            message: 'No face detected in the selected image. Please try a different image.',
            scannedImage: imagePath,
            timestamp: new Date().toLocaleString()
          };
          
          this.scanStatus = 'No face detected';
          this.showResults = true;
          
        } else {
          console.log('⚠️ ERROR RESULT:', result);
          
          this.scanResult = {
            type: 'error',
            message: result.message || result.error || 'Face detection failed',
            scannedImage: imagePath,
            timestamp: new Date().toLocaleString()
          };
          
          this.scanStatus = 'Scan failed';
          this.showResults = true;
        }
        
        console.log('🎯 Setting showResults = true');
        console.log('📊 scanResult type:', this.scanResult?.type);
        
        this.addToHistory(this.scanResult);
        
        // Force change detection for instant UI update
        setTimeout(() => {
          this.cdr.detectChanges();
          console.log('✅ UI updated instantly');
        }, 50);
      },
      error: (err) => {
        console.error('❌ Scan error:', err);
        this.isScanning = false;
        this.scanAbortController = null;
        
        // Check if it was aborted
        if (err.name === 'AbortError' || err.message?.includes('aborted')) {
          this.scanStatus = 'Scan cancelled by user';
          console.log('⏹️ Scan cancelled');
          
          this.scanResult = {
            type: 'cancelled',
            message: 'Scan was cancelled',
            progress: this.scanProgress,
            timestamp: new Date().toLocaleString()
          };
          this.showResults = true;
        } else {
          this.scanStatus = 'Scan failed';
          
          this.scanResult = {
            type: 'error',
            message: 'Failed to process image. Please try again.',
            scannedImage: imagePath,
            timestamp: new Date().toLocaleString()
          };
          this.showResults = true;
        }
        
        this.cdr.detectChanges();
      }
    });
  }

  // ================= START SCANNING ALL =================
  private startScanningAll() {
    this.isScanning = true;
    this.scanProgress = 0;
    this.scanStatus = 'Scanning all CCTV images...';
    this.showResults = false;
    this.scanAbortController = new AbortController(); // Create abort controller

    let currentIndex = 0;
    const totalImages = this.cctvImages.length;
    const results: any[] = [];
    let isCancelled = false;

    const scanNext = () => {
      // Check if cancelled
      if (isCancelled || currentIndex >= totalImages) {
        // All scans complete or cancelled
        this.isScanning = false;
        this.scanAbortController = null;
        
        if (isCancelled) {
          this.scanProgress = Math.round((currentIndex / totalImages) * 100);
          this.scanStatus = `Scan cancelled after ${currentIndex} of ${totalImages} images`;
          console.log('⏹️ Bulk scan cancelled');
        } else {
          this.scanProgress = 100;
          this.scanStatus = `Scan complete! Processed ${totalImages} images`;
        }
        
        const matchFound = results.find(r => r.type === 'match');
        if (matchFound) {
          this.scanResult = {
            type: 'bulk-match',
            totalScanned: totalImages,
            matchesFound: results.filter(r => r.type === 'match').length,
            bestMatch: matchFound,
            allResults: results,
            timestamp: new Date().toLocaleString()
          };
        } else {
          this.scanResult = {
            type: 'bulk-no-match',
            totalScanned: totalImages,
            matchesFound: 0,
            allResults: results,
            timestamp: new Date().toLocaleString()
          };
        }
        
        this.showResults = true;
        this.addToHistory(this.scanResult);
        return;
      }

      // Update progress
      this.scanProgress = Math.round((currentIndex / totalImages) * 100);
      this.scanStatus = `Scanning image ${currentIndex + 1} of ${totalImages}...`;

      // Scan current image
      const imagePath = this.cctvImages[currentIndex].image_path;
      
      this.authService.detectImage(imagePath, this.selectedCase?.person_id).subscribe({
        next: (result: any) => {
          if (result.status === 'MATCH FOUND') {
            results.push({
              type: 'match',
              confidence: result.confidence,
              name: result.name,
              personId: result.person_id,
              photo: result.photo,
              scannedImage: imagePath
            });
          } else {
            results.push({
              type: 'no-match',
              scannedImage: imagePath
            });
          }
          
          currentIndex++;
          scanNext(); // Scan next image
        },
        error: (err) => {
          console.error(`❌ Error scanning image ${currentIndex}:`, err);
          
          // Check if cancelled
          if (err.name === 'AbortError' || err.message?.includes('aborted')) {
            isCancelled = true;
          }
          
          results.push({
            type: 'error',
            scannedImage: imagePath
          });
          currentIndex++;
          if (!isCancelled) {
            scanNext(); // Continue with next image only if not cancelled
          }
        }
      });
    };

    // Start scanning
    scanNext();
  }

  // ================= ANIMATE SCANNING =================
  private animateScanning(callback: () => void) {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 25; // Faster progression
      if (progress >= 95) {
        progress = 95; // Stop at 95% until real result comes
        clearInterval(interval);
      }
      this.scanProgress = Math.round(progress);
      
      // More detailed and faster status updates
      if (progress < 20) {
        this.scanStatus = '🔍 Initializing face detector...';
      } else if (progress < 40) {
        this.scanStatus = '👤 Detecting faces in image...';
      } else if (progress < 60) {
        this.scanStatus = '🧬 Extracting facial landmarks...';
      } else if (progress < 80) {
        this.scanStatus = '📊 Computing face embeddings...';
      } else if (progress < 95) {
        this.scanStatus = '🎯 Matching with database...';
      }
    }, 100); // Faster updates (100ms instead of 200ms)

    // Call actual API faster (300ms instead of 500ms)
    setTimeout(callback, 300);
  }

  // ================= ADD TO HISTORY =================
  private addToHistory(result: any) {
    this.scanHistory.unshift(result);
    if (this.scanHistory.length > 10) {
      this.scanHistory.pop(); // Keep only last 10 scans
    }

    // Update statistics
    this.updateStatistics();
  }

  // ================= UPDATE STATISTICS =================
  private updateStatistics() {
    this.totalScans = this.scanHistory.length;
    this.matchesFound = this.scanHistory.filter(h => 
      h.type === 'match' || h.type === 'bulk-match'
    ).length;
    this.notFound = this.scanHistory.filter(h => 
      h.type === 'no-match' || h.type === 'bulk-no-match'
    ).length;

    // Calculate percentages
    if (this.totalScans > 0) {
      this.matchPercentage = Math.round((this.matchesFound / this.totalScans) * 100);
      this.notFoundPercentage = Math.round((this.notFound / this.totalScans) * 100);
    } else {
      this.matchPercentage = 0;
      this.notFoundPercentage = 0;
    }
  }

  // ================= GET IMAGE URL =================
  getImageUrl(filename: string): string {
    return this.authService.getImageUrl(filename);
  }

  // ================= GET CONFIDENCE COLOR =================
  getConfidenceColor(confidence: number): string {
    if (confidence >= 80) return '#00ff9c'; // Green
    if (confidence >= 60) return '#ffa500'; // Orange
    return '#ff4757'; // Red
  }

  // ================= GET CONFIDENCE LABEL =================
  getConfidenceLabel(confidence: number): string {
    if (confidence >= 80) return 'High Match';
    if (confidence >= 60) return 'Possible Match';
    return 'Low Match';
  }

  // ================= IMAGE PREVIEW =================
  previewImage(imageUrl: string, type: 'cctv' | 'person'): void {
    this.previewImageUrl = imageUrl;
    this.previewImageType = type;
    this.showImagePreview = true;
  }

  closeImagePreview(): void {
    this.showImagePreview = false;
    this.previewImageUrl = '';
    this.previewImageType = '';
  }

  // ================= ALERT MANAGEMENT =================
  dismissAlert(alertId: number): void {
    this.activeAlerts = this.activeAlerts.filter(a => a.id !== alertId);
    if (this.activeAlerts.length === 0) {
      this.showAlertPanel = false;
    }
  }

  clearAllAlerts(): void {
    this.activeAlerts = [];
    this.showAlertPanel = false;
    this.alertService.clearAlerts();
  }

  viewAlertDetails(alert: any): void {
    // Navigate to specific case or show more details
    console.log('Alert details:', alert);
  }

  // ================= ADVANCED FACE RECOGNITION =================
  onImageSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedImageFile = file;
      
      // Create preview URL
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.previewImageUrl = e.target.result;
        this.showImagePreview = true;
        this.previewImageType = 'person';
      };
      reader.readAsDataURL(file);
      
      console.log('✅ Image selected:', file.name);
    }
  }

  runAdvancedRecognition(): void {
    if (!this.selectedImageFile) {
      alert('⚠️ Please select an image first');
      return;
    }

    this.isScanning = true;
    this.scanProgress = 0;
    this.scanStatus = '🧠 Loading CNN model...';
    this.showResults = false;

    // Simulate model loading
    setTimeout(() => {
      this.scanProgress = 20;
      this.scanStatus = '🔍 Detecting faces...';
    }, 500);

    setTimeout(() => {
      this.scanProgress = 50;
      this.scanStatus = '🧬 Extracting facial embeddings...';
    }, 1000);

    setTimeout(() => {
      this.scanProgress = 80;
      this.scanStatus = '🎯 Comparing with database...';
    }, 1500);

    // Call advanced recognition API
    this.authService.recognizeFace(this.selectedImageFile).subscribe({
      next: (result: any) => {
        console.log('🎯 Advanced recognition result:', result);
        
        this.isScanning = false;
        this.scanProgress = 100;
        this.scanStatus = '✅ Recognition complete!';
        
        this.advancedRecognitionResult = result.data;
        this.showAdvancedRecognition = true;
        this.showResults = true;
        
        // Check for matches and show alerts
        if (result.data.matches && result.data.matches.length > 0) {
          const match = result.data.matches[0];
          if (match.match_found && match.person_info) {
            // Show match alert
            const alert = this.alertService.showMatchAlert(
              `Person ${match.person_id}`,
              match.confidence,
              match.person_id,
              match.person_info.image_path
            );
            this.activeAlerts.unshift(alert);
            this.showAlertPanel = true;
            
            setTimeout(() => {
              this.showAlertPanel = false;
            }, 10000);
          }
        }
        
        this.addToHistory({
          type: result.data.matches?.[0]?.match_found ? 'match' : 'no-match',
          confidence: result.data.matches?.[0]?.confidence || 0,
          timestamp: new Date().toLocaleString()
        });
      },
      error: (err) => {
        console.error('❌ Recognition error:', err);
        this.isScanning = false;
        this.scanStatus = '❌ Recognition failed';
        alert('Failed to perform recognition. Please try again.');
      }
    });
  }

  encodeDataset(): void {
    if (confirm('This will re-encode all missing persons in the dataset. Continue?')) {
      this.authService.encodeDataset().subscribe({
        next: (result: any) => {
          alert(`✅ ${result.message}`);
          console.log('Dataset encoded:', result);
        },
        error: (err) => {
          console.error('❌ Encoding error:', err);
          alert('Failed to encode dataset');
        }
      });
    }
  }

  // ================= CANCEL SCANNING =================
  cancelScanning(): void {
    if (this.isScanning) {
      // Abort the HTTP request
      if (this.scanAbortController) {
        this.scanAbortController.abort();
        this.scanAbortController = null;
      }
      
      this.isScanning = false;
      this.scanStatus = 'Scan cancelled by user';
      console.log('⏹️ Scanning cancelled');
      
      // Show cancelled result
      this.scanResult = {
        type: 'cancelled',
        message: 'Scan was cancelled by user',
        progress: this.scanProgress,
        timestamp: new Date().toLocaleString()
      };
      this.showResults = true;
    }
  }
}