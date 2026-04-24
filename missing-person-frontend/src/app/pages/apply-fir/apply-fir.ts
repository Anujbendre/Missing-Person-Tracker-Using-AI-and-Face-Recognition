import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-apply-fir',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './apply-fir.html',
  styleUrls: ['./apply-fir.css']
})
export class ApplyFIRComponent {

  firData = {
    full_name: '',
    email: '',
    phone: '',
    incident_type: '',
    location: '',
    description: '',
    accused: '',
    delay_reason: '',
    property: '',
    date: '',
    time: ''
  };

  constructor(
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  submitFIR() {
    // Validation
    if (!this.firData.full_name.trim() || !this.firData.email.trim() || !this.firData.phone.trim()) {
      alert('⚠️ Please fill required fields (Name, Email, Phone)');
      return;
    }

    const formData = new FormData();

    Object.keys(this.firData).forEach(key => {
      const value = (this.firData as any)[key];
      formData.append(key, value || '');
    });

    this.authService.applyFIR(formData).subscribe({
      next: (response: any) => {
        console.log('✅ FIR submitted:', response);
        alert("✅ FIR submitted successfully");
        this.resetForm();
      },
      error: (err) => {
        console.error('❌ FIR submission error:', err);
        const errorMsg = err.error?.error || 'Error submitting FIR';
        alert(`❌ ${errorMsg}`);
      }
    });
  }

  resetForm() {
    this.firData = {
      full_name: '',
      email: '',
      phone: '',
      incident_type: '',
      location: '',
      description: '',
      accused: '',
      delay_reason: '',
      property: '',
      date: '',
      time: ''
    };

    this.cdr.detectChanges();
  }
}