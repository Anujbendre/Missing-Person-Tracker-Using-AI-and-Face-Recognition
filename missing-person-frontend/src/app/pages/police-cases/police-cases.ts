import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-police-cases',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './police-cases.html',
  styleUrls: ['./police-cases.css']
})
export class PoliceCasesComponent implements OnInit {

  showModal: boolean = false;
  selectedDescription: string = '';
  selectedImage: string | null = null;
  imageLoadError: boolean = false;

  cases: any[] = [];
  filteredCases: any[] = [];
  loading: boolean = true;
  errorMsg: string = '';

  constructor(private authService: AuthService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadCases();
  }

  // ================= LOAD CASES =================
loadCases(): void {
  this.loading = true;

  this.authService.getPoliceCases().subscribe({
    next: (res: any) => {
      console.log("🔥 FRONTEND DATA:", res);

      this.cases = res?.data || [];
      this.filteredCases = [...this.cases];

      this.loading = false;

      // 🔥 FORCE UI UPDATE (FINAL FIX)
      this.cdr.detectChanges();
    },

    error: (err) => {
      console.error("❌ ERROR:", err);
      this.loading = false;
    }
  });
}

  // ================= SEARCH =================
filterLocation(event: Event): void {
  const input = event.target as HTMLInputElement;
  const value = input.value.trim().toLowerCase();

  this.filteredCases = this.cases.filter(c =>
    c.full_name?.toLowerCase().includes(value) ||       // 🔥 search by name
    c.last_seen_location?.toLowerCase().includes(value) || // 🔥 search by location
    c.status?.toLowerCase().includes(value) ||          // 🔥 search by status
    c.person_id?.toString().includes(value)             // 🔥 search by ID
  );
}

  // ================= IMAGE VIEW =================
  viewImage(img: string): void {
    if (!img) {
      alert("No image available");
      return;
    }

    // Use AuthService to get proper image URL
    const url = this.authService.getImageUrl(img);

    console.log("🖼️ IMAGE FILENAME:", img);
    console.log("🖼️ IMAGE URL:", url);
    console.log("🖼️ FULL URL:", `${this.authService['baseUrl']}/uploads/${img}`);

    // Reset error state
    this.imageLoadError = false;
    
    // Show in popup
    this.selectedImage = url;
  }

  closeImage(): void {
    this.selectedImage = null;
    this.imageLoadError = false;
  }

  onImageError(): void {
    console.error('❌ Image failed to load:', this.selectedImage);
    this.imageLoadError = true;
  }

  onImageLoad(): void {
    console.log('✅ Image loaded successfully');
    this.imageLoadError = false;
  }
  // ================= STATUS UPDATE =================
  updateStatus(id: number, status: string): void {
    if (!status) return;

    this.authService.updateCaseStatus(id, status).subscribe({
      next: () => {
        alert("✅ Status updated successfully");
        this.loadCases();
      },
      error: (err) => {
        console.error("❌ Status update error:", err);
        alert("❌ Failed to update status");
      }
    });
  }

  openDescription(desc: string) {
  this.selectedDescription = desc || "No description available";
  this.showModal = true;
}

closeModal() {
  this.showModal = false;
}
}