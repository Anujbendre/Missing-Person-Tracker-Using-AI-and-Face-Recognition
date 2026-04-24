import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router,RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

// Material
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-police-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    RouterModule
  ],
  templateUrl: './police-login.html',
  styleUrls: ['./police-login.css']
})
export class PoliceLoginComponent {

  data: any = {};

  constructor(private http: HttpClient, private router: Router) {}

  login() {
    if (!this.data.email || !this.data.password) {
      alert("Please enter email and password ❌");
      return;
    }

    console.log('Attempting login with:', this.data.email);

    this.http.post('http://localhost:8000/police/login', {
      email: this.data.email,
      password: this.data.password
    }).subscribe({
      next: (res: any) => {
        console.log('Login response:', res);
        console.log('Response keys:', Object.keys(res));

        // Check if there's an error in the response
        if (res.error) {
          console.error('Login error from server:', res.error);
          alert(res.error + " ❌");
          return;
        }

        // More flexible check - accept either access_token or just message with user
        if (res.message) {
          console.log('Login message received:', res.message);
          
          // Check if we got a token
          if (res.access_token) {
            console.log('Token received, storing...');
            // ✅ STORE JWT TOKEN (Required for auth guard)
            localStorage.setItem('token', res.access_token);
          } else {
            console.warn('No access_token in response! This will cause auth issues.');
            console.log('Full response:', JSON.stringify(res, null, 2));
          }

          // ✅ STORE USER INFO
          if (res.user) {
            localStorage.setItem('policeUser', JSON.stringify(res.user));
            console.log('User stored:', localStorage.getItem('policeUser'));
          }
          
          alert("Login Successful ✅\nWelcome, " + (res.user?.name || 'Officer') + "!");

          // 🔥 REDIRECT TO DASHBOARD - Use window.location for guaranteed navigation
          setTimeout(() => {
            console.log('Navigating to police-dashboard...');
            window.location.href = '/police-dashboard';
          }, 300);

        } else {
          console.error('Invalid response format:', res);
          alert("Login Failed: Invalid response ❌");
        }
      },
      error: (err) => {
        console.error('HTTP error:', err);
        if (err.status === 401) {
          alert("Invalid Email or Password ❌");
        } else if (err.status === 0) {
          alert("Cannot connect to server.\nPlease ensure backend is running on port 8000 ❌");
        } else {
          alert("Server Error: " + (err.error?.error || err.message || 'Unknown error') + " ❌");
        }
      }
    });
  }

  close() {
    window.history.back();
  }
}