import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-police-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './police-dashboard.html',
  styleUrls: ['./police-dashboard.css']
})
export class PoliceDashboardComponent implements OnInit {

  // Statistics
  totalCases: number = 0;
  activeCases: number = 0;
  closedCases: number = 0;
  matchesFound: number = 0;
  pendingAlerts: number = 0;
  
  // Advanced Analytics
  resolutionRate: number = 0;
  avgDetectionTime: string = 'N/A';
  trendingLocations: any[] = [];
  dailyActivity: any[] = [];
  ageGroupStats: any[] = [];
  genderStats: any[] = [];
  weeklyTrend: number = 0;
  monthlyTrend: number = 0;

  // Data
  recentCases: any[] = [];
  recentDetections: any[] = [];
  loading: boolean = false;
  statsLoading: boolean = false;
  casesLoading: boolean = false;
  detectionsLoading: boolean = false;

  // Profile
  policeUser: any = null;
  showProfileMenu: boolean = false;

  // News
  newsItems: any[] = [
    {
      title: 'New AI Model Deployed',
      content: 'Face recognition accuracy improved by 15%',
      time: '2 hours ago',
      type: 'success'
    },
    {
      title: 'Critical: Missing Child Case',
      content: 'Case #1234 requires immediate attention',
      time: '5 hours ago',
      type: 'urgent'
    },
    {
      title: 'CCTV Camera Offline',
      content: 'Camera #45 at Station Road is not responding',
      time: '1 day ago',
      type: 'warning'
    },
    {
      title: 'System Update',
      content: 'Scheduled maintenance on Sunday 2AM-4AM',
      time: '2 days ago',
      type: 'info'
    },
    {
      title: 'Match Found: Case #987',
      content: 'AI detected potential match for Rahul Sharma',
      time: '3 days ago',
      type: 'success'
    }
  ];

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.loadDashboardData();
    this.loadUserProfile();
  }

  // ================= LOAD USER PROFILE =================
  loadUserProfile() {
    const userStr = localStorage.getItem('policeUser');
    console.log('Raw policeUser from localStorage:', userStr);
    if (userStr) {
      try {
        this.policeUser = JSON.parse(userStr);
        console.log('Parsed policeUser:', this.policeUser);
      } catch (e) {
        console.error('Error parsing user data:', e);
        this.policeUser = null;
      }
    } else {
      console.warn('No policeUser found in localStorage');
    }
  }

  // ================= LOAD ALL DASHBOARD DATA =================
  loadDashboardData() {
    // Don't block the entire dashboard - load data in background
    this.statsLoading = true;
    this.casesLoading = true;
    this.detectionsLoading = true;

    // Load all cases
    this.authService.getAllCases().subscribe({
      next: (res: any) => {
        const cases = res?.data || [];
        this.totalCases = cases.length;
        
        // Calculate active and closed
        this.activeCases = cases.filter((c: any) => 
          c.status === 'MISSING' || c.status === 'OPEN' || c.status === 'IN_PROGRESS'
        ).length;
        
        this.closedCases = cases.filter((c: any) => 
          c.status === 'FOUND' || c.status === 'CLOSED'
        ).length;

        // Recent cases
        this.recentCases = cases.slice(0, 5);
        
        this.casesLoading = false;
      },
      error: (err) => {
        console.error('Error loading cases:', err);
        this.casesLoading = false;
        // Set defaults on error
        this.totalCases = 0;
        this.activeCases = 0;
        this.closedCases = 0;
      }
    });

    // Load analytics
    this.authService.getAnalytics().subscribe({
      next: (res: any) => {
        const analytics = res?.data || res || {};
        this.matchesFound = analytics.recent_matches || analytics.matches_found || 0;
        this.pendingAlerts = analytics.pending_alerts || 0;
        this.statsLoading = false;
      },
      error: (err) => {
        console.error('Error loading analytics:', err);
        this.statsLoading = false;
        // Set defaults on error
        this.matchesFound = 0;
        this.pendingAlerts = 0;
      }
    });

    // Load recent detections
    this.authService.getDetectionLogs().subscribe({
      next: (res: any) => {
        const logs = res?.data || res || [];
        this.recentDetections = logs.slice(0, 5);
        this.detectionsLoading = false;
      },
      error: (err) => {
        console.error('Error loading detections:', err);
        this.detectionsLoading = false;
        // Fallback to empty array
        this.recentDetections = [];
      }
    });
  }

  // ================= GET STATUS COLOR =================
  getStatusColor(status: string): string {
    switch(status?.toUpperCase()) {
      case 'MISSING':
      case 'OPEN':
        return '#ff4757';
      case 'IN_PROGRESS':
        return '#ffa500';
      case 'FOUND':
      case 'CLOSED':
        return '#00ff9c';
      default:
        return '#a0aec0';
    }
  }

  // ================= GET STATUS ICON =================
  getStatusIcon(status: string): string {
    switch(status?.toUpperCase()) {
      case 'MISSING':
      case 'OPEN':
        return '🔍';
      case 'IN_PROGRESS':
        return '⏳';
      case 'FOUND':
      case 'CLOSED':
        return '✅';
      default:
        return '❓';
    }
  }

  // ================= NAVIGATE TO SECTION =================
  navigateTo(path: string) {
    // This would navigate using router if needed
    console.log('Navigate to:', path);
  }

  // ================= REFRESH DATA =================
  refreshData() {
    this.loadDashboardData();
  }

  // ================= GET NEWS COLOR =================
  getNewsColor(type: string): string {
    switch(type) {
      case 'urgent':
        return '#ff4757';
      case 'warning':
        return '#ffa500';
      case 'success':
        return '#00ff9c';
      case 'info':
      default:
        return '#00c6ff';
    }
  }

  // ================= GET NEWS ICON =================
  getNewsIcon(type: string): string {
    switch(type) {
      case 'urgent':
        return '🚨';
      case 'warning':
        return '⚠️';
      case 'success':
        return '✅';
      case 'info':
      default:
        return 'ℹ️';
    }
  }

  // ================= TOGGLE PROFILE MENU =================
  toggleProfileMenu() {
    this.showProfileMenu = !this.showProfileMenu;
  }

  // ================= CLOSE PROFILE MENU =================
  closeProfileMenu() {
    this.showProfileMenu = false;
  }

  // ================= CLOSE PROFILE MENU ON OUTSIDE CLICK =================
  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event) {
    const target = event.target as HTMLElement;
    // Close dropdown if click is outside profile container
    if (!target.closest('.gov-profile-container')) {
      this.closeProfileMenu();
    }
  }

  // ================= LOGOUT =================
  logout() {
    if (confirm('Are you sure you want to logout?')) {
      localStorage.removeItem('token');
      localStorage.removeItem('policeUser');
      window.location.href = '/police-login';
    }
  }
}
