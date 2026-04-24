import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-download-fir',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './download-fir.html',
  styleUrls: ['./download-fir.css']
})
export class DownloadFIRComponent {

  // ===== DATA =====
  firs: any[] = [];
  loading = false;

  // ===== OTP =====
  mobile: string = '';
  otp: string = '';
  otpSent = false;
  isVerified = false;

  constructor(private http: HttpClient) {}

  // ===== SEND OTP =====
  sendOtp() {
    const formData = new FormData();
    formData.append('mobile', this.mobile.trim());

    this.http.post('http://127.0.0.1:8000/send-otp', formData)
      .subscribe({
        next: () => {
          alert("OTP sent (check backend)");
          this.otpSent = true;
        },
        error: () => {
          alert("Mobile not found");
        }
      });
  }

  // ===== VERIFY OTP =====
  verifyOtp() {
    const formData = new FormData();
    formData.append('mobile', this.mobile.trim());
    formData.append('otp', this.otp);

    this.http.post('http://127.0.0.1:8000/verify-otp', formData)
      .subscribe((res: any) => {

        if (res.success) {
          this.isVerified = true;
          this.loadFIRs();
        } else {
          alert("Invalid OTP");
        }

      });
  }

  // ===== LOAD FIRs =====
  loadFIRs() {
    this.loading = true;

    this.http.get(`http://127.0.0.1:8000/my-cases-by-mobile?mobile=${this.mobile}`)
      .subscribe({
        next: (res: any) => {
          this.firs = res.data || [];
          this.loading = false;
        },
        error: () => {
          this.loading = false;
        }
      });
  }

  // ===== DOWNLOAD =====
  download(id: number) {
    window.open(`http://127.0.0.1:8000/download-fir/${id}`, '_blank');
  }
}