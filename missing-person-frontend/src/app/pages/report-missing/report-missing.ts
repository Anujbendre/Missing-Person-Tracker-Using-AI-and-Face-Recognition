import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-report-missing',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './report-missing.html',
  styleUrls: ['./report-missing.css']
})
export class ReportMissingComponent {

  // ===== FORM DATA =====
  formData = {
    name: '',
    age: '',
    gender: '',
    location: '',
    description: '',
    reporter_name: '',
    reporter_mobile: ''
  };

  // ===== FILE =====
  selectedFile: File | null = null;

  // ===== LOADING STATE =====
  loading = false;

  constructor(private authService: AuthService) {}

  // ===== FILE SELECT =====
  onFileSelect(event: any) {
    if (event.target.files && event.target.files.length > 0) {
      this.selectedFile = event.target.files[0];
    }
  }

  // ===== SUBMIT =====
  onSubmit() {

    // 🔴 VALIDATION
    if (!this.formData.name.trim() ||
        !this.formData.age ||
        !this.formData.reporter_mobile.trim()) {

      alert("⚠️ Please fill required fields (Name, Age, Mobile)");
      return;
    }

    // 🔴 MOBILE VALIDATION (10 digits)
    if (this.formData.reporter_mobile.length !== 10) {
      alert("⚠️ Enter valid 10-digit mobile number");
      return;
    }

    this.loading = true;

    const formDataToSend = new FormData();

    formDataToSend.append('name', this.formData.name.trim());
    formDataToSend.append('age', this.formData.age.toString());
    formDataToSend.append('gender', this.formData.gender || '');
    formDataToSend.append('location', this.formData.location || '');
    formDataToSend.append('description', this.formData.description || '');
    formDataToSend.append('reporter_name', this.formData.reporter_name.trim());
    formDataToSend.append('reporter_mobile', this.formData.reporter_mobile.trim());

    if (this.selectedFile) {
      formDataToSend.append('file', this.selectedFile);
    }

    this.authService.reportMissing(formDataToSend).subscribe({
      next: (response: any) => {
        this.loading = false;
        console.log('✅ Report submitted:', response);
        alert("✅ Report submitted successfully");

        // RESET FORM
        this.formData = {
          name: '',
          age: '',
          gender: '',
          location: '',
          description: '',
          reporter_name: '',
          reporter_mobile: ''
        };

        this.selectedFile = null;
      },

      error: (err) => {
        this.loading = false;
        console.error('❌ Submission error:', err);
        const errorMsg = err.error?.error || 'Failed to submit report';
        alert(`❌ ${errorMsg}`);
      }
    });
  }

  downloadFIR(id: number) {
    window.open(`http://127.0.0.1:8000/download-fir/${id}`, '_blank');
  }
}
