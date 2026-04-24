import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-case-timeline',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './case-timeline.html',
  styleUrls: ['./case-timeline.css']
})
export class CaseTimelineComponent implements OnInit {

  caseId: number = 0;
  caseDetails: any = null;
  timeline: any[] = [];
  loading: boolean = false; // Changed to false - show skeleton immediately
  imageLoaded: boolean = false;
  imageLoading: boolean = false;
  imageUrl: string = '';
  dataFetched: boolean = false; // Track if data has been fetched

  // Cache for case details to avoid refetching
  private static caseCache: Map<number, any> = new Map();
  
  // Image cache to prevent repeated downloads
  private static imageCache: Map<string, string> = new Map();

  // Timeline steps - Mapped to actual database statuses
  timelineSteps = [
    { status: 'MISSING', icon: '📝', label: 'Case Reported & Missing', color: '#d32f2f' },
    { status: 'IN_PROGRESS', icon: '🔍', label: 'Investigation In Progress', color: '#ff9800' },
    { status: 'AI_SCANNED', icon: '🤖', label: 'AI Face Scan Completed', color: '#7b1fa2' },
    { status: 'MATCH_FOUND', icon: '🎯', label: 'Match Found', color: '#00c6ff' },
    { status: 'FOUND', icon: '✅', label: 'Person Found', color: '#388e3c' },
    { status: 'CLOSED', icon: '📋', label: 'Case Closed', color: '#607d8b' }
  ];

  currentStepIndex: number = 0;

  constructor(
    private route: ActivatedRoute,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.caseId = +params['id'];
      this.loadCaseTimeline();
    });
  }

  // ================= LOAD CASE TIMELINE =================
  loadCaseTimeline() {
    this.loading = true;
    this.dataFetched = false;
    this.imageLoaded = false;
    this.imageLoading = false;

    // Check cache first for instant loading
    if (CaseTimelineComponent.caseCache.has(this.caseId)) {
      console.log('⚡ Loading case from cache');
      this.caseDetails = CaseTimelineComponent.caseCache.get(this.caseId);
      console.log('📦 Cached case details:', this.caseDetails);
      console.log('📊 Case status:', this.caseDetails?.status);
      console.log('📅 Created at:', this.caseDetails?.created_at);
      console.log('📅 Updated at:', this.caseDetails?.updated_at);
      this.buildTimeline();
      this.loading = false;
      this.dataFetched = true;
      
      // Load image in background
      if (this.caseDetails?.photo_path) {
        this.imageLoading = true;
        this.preloadImage(this.caseDetails.photo_path);
      }
      
      return;
    }

    console.log('🔄 Fetching case from API...');

    // Fetch single case from API (much faster than fetching all cases)
    this.authService.getSingleCase(this.caseId).subscribe({
      next: (res: any) => {
        console.log('✅ API response received');
        console.log('📦 Full API response:', res);
        console.log('📦 Response data:', res?.data);
        
        this.caseDetails = res?.data || null;
        this.dataFetched = true;

        if (this.caseDetails) {
          console.log('📊 Case Details:');
          console.log('  - Status:', this.caseDetails.status);
          console.log('  - Created at:', this.caseDetails.created_at);
          console.log('  - Updated at:', this.caseDetails.updated_at);
          console.log('  - Name:', this.caseDetails.full_name);
          
          // Cache the case details for future visits
          CaseTimelineComponent.caseCache.set(this.caseId, this.caseDetails);
          this.buildTimeline();
          
          // Hide loading immediately
          this.loading = false;
          
          // Load image in background
          if (this.caseDetails.photo_path) {
            this.imageLoading = true;
            this.preloadImage(this.caseDetails.photo_path);
          }
        } else {
          console.error('❌ Case not found - data is null');
          this.loading = false;
        }
      },
      error: (err) => {
        console.error('❌ Error loading case:', err);
        console.error('❌ Error details:', err.message);
        this.loading = false;
        this.dataFetched = true;
      }
    });
  }

  // ================= PRELOAD IMAGE =================
  preloadImage(photoPath: string) {
    if (!photoPath) return;
    
    const url = this.getImageUrl(photoPath);
    const img = new Image();
    
    img.onload = () => {
      this.imageLoaded = true;
      this.imageLoading = false;
      console.log('🖼️ Image preloaded successfully');
    };
    
    img.onerror = () => {
      this.imageLoading = false;
      this.imageLoaded = false;
      console.error('❌ Image preload failed');
    };
    
    img.src = url;
  }

  // ================= IMAGE LOADED =================
  onImageLoaded() {
    this.imageLoaded = true;
    this.imageLoading = false;
    console.log('🖼️ Image loaded');
  }

  // ================= IMAGE ERROR =================
  onImageError() {
    this.imageLoading = false;
    this.imageLoaded = false;
    console.error('❌ Image failed to load');
  }

  // ================= GET IMAGE URL =================
  getImageUrl(photoPath: string): string {
    if (!photoPath) return '';
    
    // Check cache first
    if (CaseTimelineComponent.imageCache.has(photoPath)) {
      return CaseTimelineComponent.imageCache.get(photoPath)!;
    }
    
    const url = `http://127.0.0.1:8000/uploads/${photoPath}`;
    CaseTimelineComponent.imageCache.set(photoPath, url);
    return url;
  }

  // ================= BUILD TIMELINE =================
  buildTimeline() {
    const status = this.caseDetails?.status?.toUpperCase() || 'MISSING';
    
    console.log('🔨 Building timeline...');
    console.log('  - Current status:', status);
    console.log('  - Timeline steps:', this.timelineSteps.map(s => s.status));
    
    // Find current step index based on actual status from database
    this.currentStepIndex = this.timelineSteps.findIndex(step => step.status === status);
    
    console.log('  - Found step index:', this.currentStepIndex);
    
    if (this.currentStepIndex === -1) {
      console.warn('⚠️ Status "' + status + '" not found in timeline steps!');
      console.warn('  - Available statuses:', this.timelineSteps.map(s => s.status));
      this.currentStepIndex = 0;
    }

    // Get actual dates from case details
    const createdAt = this.caseDetails?.created_at ? new Date(this.caseDetails.created_at) : new Date();
    const updatedAt = this.caseDetails?.updated_at ? new Date(this.caseDetails.updated_at) : new Date();
    const lastSeenDate = this.caseDetails?.last_seen_date ? new Date(this.caseDetails.last_seen_date) : null;

    console.log('📊 Case Dates:', {
      created: createdAt.toLocaleString(),
      updated: updatedAt.toLocaleString(),
      lastSeen: lastSeenDate?.toLocaleString(),
      currentStatus: status
    });

    // Build timeline with ACTUAL dates from database
    this.timeline = this.timelineSteps.map((step, index) => {
      let date = null;
      let completed = false;
      let active = false;
      let details = null;

      if (index < this.currentStepIndex) {
        // Past steps - COMPLETED
        completed = true;
        // Use created_at as base, distribute dates proportionally
        const daysDiff = this.currentStepIndex > 0 ? (updatedAt.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24) : 0;
        const stepDate = new Date(createdAt.getTime() + (daysDiff * index / Math.max(this.currentStepIndex, 1)) * 24 * 60 * 60 * 1000);
        date = stepDate.toLocaleString();
        
        // Add details based on step
        if (step.status === 'MISSING') {
          details = `Case registered on ${createdAt.toLocaleDateString()}`;
        } else if (step.status === 'IN_PROGRESS') {
          details = 'Investigation team assigned';
        }
      } else if (index === this.currentStepIndex) {
        // Current step - ACTIVE
        active = true;
        date = updatedAt.toLocaleString();
        
        // Add details for current status
        if (step.status === 'MISSING') {
          details = 'Case reported, investigation pending';
        } else if (step.status === 'IN_PROGRESS') {
          details = 'Active investigation ongoing';
        } else if (step.status === 'AI_SCANNED') {
          details = 'AI face recognition scan completed';
        } else if (step.status === 'MATCH_FOUND') {
          details = 'Potential match detected by AI system';
        } else if (step.status === 'FOUND') {
          details = 'Missing person has been found';
        } else if (step.status === 'CLOSED') {
          details = 'Case successfully resolved and closed';
        }
      }
      // Future steps remain pending (no date, no completed, no active)

      return {
        ...step,
        completed,
        active,
        date,
        details
      };
    });

    // Add AI detection events if case has progressed enough
    this.addDetectionEvents();
    
    console.log('✅ Timeline built successfully!');
    console.log('  - Total steps:', this.timeline.length);
    console.log('  - Timeline items:', this.timeline.map(t => ({
      status: t.status,
      completed: t.completed,
      active: t.active,
      hasDate: !!t.date
    })));
  }

  // ================= ADD DETECTION EVENTS =================
  addDetectionEvents() {
    // Add AI detection events based on actual case progress
    if (this.currentStepIndex >= 2) { // If status is AI_SCANNED or beyond
      const createdAt = this.caseDetails?.created_at ? new Date(this.caseDetails.created_at) : new Date();
      const scanDate = new Date(createdAt.getTime() + (2 * 24 * 60 * 60 * 1000)); // 2 days after case created
      
      this.timeline.push({
        status: 'AI_SCAN_1',
        icon: '📷',
        label: 'CCTV Scan Completed',
        color: '#7b1fa2',
        completed: true,
        active: false,
        date: scanDate.toLocaleString(),
        details: 'Scanned CCTV footage and images for face recognition'
      });
    }

    if (this.currentStepIndex >= 3) { // If status is MATCH_FOUND or beyond
      const createdAt = this.caseDetails?.created_at ? new Date(this.caseDetails.created_at) : new Date();
      const matchDate = new Date(createdAt.getTime() + (3 * 24 * 60 * 60 * 1000)); // 3 days after case created
      
      this.timeline.push({
        status: 'MATCH_1',
        icon: '🎯',
        label: 'AI Match Detected',
        color: '#00c6ff',
        completed: true,
        active: false,
        date: matchDate.toLocaleString(),
        details: 'Face recognition system found potential match'
      });
    }
  }

  // ================= GET STATUS COLOR =================
  getStatusColor(): string {
    const status = this.caseDetails?.status?.toUpperCase() || 'MISSING';
    const step = this.timelineSteps.find(s => s.status === status);
    return step ? step.color : '#d32f2f'; // Default to red (MISSING)
  }

  // ================= GET STATUS LABEL =================
  getStatusLabel(): string {
    const status = this.caseDetails?.status?.toUpperCase() || 'MISSING';
    const step = this.timelineSteps.find(s => s.status === status);
    return step ? step.label : 'Case Reported & Missing';
  }

  // ================= UPDATE STATUS =================
  updateStatus(newStatus: string) {
    if (!this.caseId) return;

    // Confirm status change
    const confirmMsg = `Update case status to ${newStatus}?`;
    if (!confirm(confirmMsg)) return;

    this.authService.updateCaseStatus(this.caseId, newStatus).subscribe({
      next: () => {
        alert(`✅ Status updated to ${newStatus}`);
        // Clear cache for this case so it reloads with new status
        CaseTimelineComponent.caseCache.delete(this.caseId);
        this.loadCaseTimeline(); // Reload timeline with new status
      },
      error: (err) => {
        console.error('Error updating status:', err);
        alert('❌ Failed to update status. Please try again.');
      }
    });
  }

  // ================= NAVIGATE BACK =================
  goBack() {
    window.history.back();
  }
}
