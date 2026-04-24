import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-view-missing',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatIconModule, FormsModule],
  templateUrl: './view-missing.html',
  styleUrls: ['./view-missing.css']
})
export class ViewMissingComponent implements OnInit {

  displayedColumns: string[] = [
    'person_id',
    'full_name',
    'age',
    'gender',
    'last_seen_location',
    'description',
    'photo_path',
    'status',
    'reporter_mobile'
  ];
  
  cases: any[] = [];
  loading = false;
  selectedImage: string | null = null;
  selectedCase: any = null;

  mobile: string = '';
  otp: string = '';
  otpSent = false;
  generatedOtp: string = '';
  isVerified: boolean = false;

  constructor(
    private cdr: ChangeDetectorRef,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    // Auto-load all cases if needed
    // this.loadAllCases();
  }

  // ✅ SEND OTP
  sendOtp() {
    const mobile = this.mobile.trim();

    if (!mobile || mobile.length !== 10) {
      alert('⚠️ Please enter a valid 10-digit mobile number');
      return;
    }

    this.authService.sendOTP(mobile).subscribe({
      next: (res: any) => {
        this.otpSent = true;
        this.generatedOtp = res.otp;
        console.log('OTP sent:', res.otp);
      },
      error: (err) => {
        console.error('Failed to send OTP:', err);
        alert('Failed to send OTP ❌');
      }
    });
  }

  // ✅ VERIFY OTP
  verifyOtp() {
    const body = {
      mobile: this.mobile.trim(),
      otp: Number(this.otp)
    };

    this.authService.verifyOTP(body.mobile, body.otp).subscribe({
      next: (res: any) => {
        if (!res.exists) {
          alert('No records found ❌');
          this.cases = [];
          return;
        }

        // ✅ CLOSE POPUP
        this.isVerified = true;

        // ✅ LOAD DATA
        this.cases = res.data;
        console.log('✅ Cases loaded:', this.cases);
      },
      error: (err) => {
        console.error('Invalid OTP:', err);
        alert('Invalid OTP ❌');
      }
    });
  }

  // ✅ LOAD ALL CASES (for police/admin)
  loadAllCases(): void {
    this.loading = true;

    this.authService.getAllCases().subscribe({
      next: (res: any) => {
        console.log('All Cases:', res);
        this.cases = res?.data || [];
        this.loading = false;
        this.isVerified = true;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading cases:', err);
        alert('Failed to load cases');
        this.loading = false;
      }
    });
  }

  // ✅ IMAGE VIEW
  viewImage(path: string) {
    if (!path) {
      alert('No image available ❌');
      return;
    }

    console.log('Image path:', path);
    this.selectedImage = path;
  }

  closeImage(): void {
    this.selectedImage = null;
  }

  // ✅ DESCRIPTION VIEW
  viewDescription(caseData: any) {
    this.selectedCase = caseData;
  }

  closeDescription(): void {
    this.selectedCase = null;
  }

  // ✅ IMAGE URL
  getImageUrl(path: string) {
    return this.authService.getImageUrl(path);
  }
}