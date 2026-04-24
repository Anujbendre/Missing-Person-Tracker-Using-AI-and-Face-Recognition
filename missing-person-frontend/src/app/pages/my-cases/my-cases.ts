import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-my-cases',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-cases.html',
  styleUrls: ['./my-cases.css']
})
export class MyCasesComponent implements OnInit {

  cases: any[] = [];
  loading = true;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.loadCases();
  }

  loadCases(): void {
    this.authService.getAllCases().subscribe({
      next: (res: any) => {
        console.log("My Cases:", res);

        this.cases = res?.data || [];
        this.loading = false;
      },
      error: (err) => {
        console.error(err);
        this.loading = false;
      }
    });
  }

  selectedImage: string | null = null;

  viewImage(img: string) {
    if (!img) {
      alert("No image available");
      return;
    }
    // Use AuthService to get proper image URL
    this.selectedImage = this.authService.getImageUrl(img);
  }

  closeImage() {
    this.selectedImage = null;
  }
}