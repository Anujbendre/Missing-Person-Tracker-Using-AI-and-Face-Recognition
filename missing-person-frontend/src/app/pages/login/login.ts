import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

/* Material */
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-login',
  standalone: true,
  templateUrl: './login.html',
  styleUrls: ['./login.css'],
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ]
})
export class LoginComponent {

  loginForm: FormGroup;
  isLoading = false; // ✅ added for UX

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    public dialogRef: MatDialogRef<LoginComponent>
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  close() {
    this.dialogRef.close();
  }

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading = true;

    this.authService.login(this.loginForm.value).subscribe({
      next: (res: any) => {
        console.log("Login Success:", res);

        // ✅ CHECK TOKEN EXISTS
        if (!res.access_token) {
          alert("Invalid response from server ❌");
          this.isLoading = false;
          return;
        }

        // ✅ SAVE TOKEN
        localStorage.setItem('token', res.access_token);

        // ✅ SAFE TOKEN DECODE
        let payload: any;
        try {
          payload = JSON.parse(atob(res.access_token.split('.')[1]));
          console.log("User Payload:", payload);
        } catch (e) {
          console.error("Token decode error", e);
          alert("Invalid token ❌");
          this.isLoading = false;
          return;
        }

        alert("Login Successful ✅");

        // ✅ CLOSE DIALOG
        this.dialogRef.close();

        // 🚀 ROLE-BASED REDIRECT (SAFE)
        setTimeout(() => {
          if (payload.role_id === 2) {
            this.router.navigate(['/police-dashboard']);
          } 
          else if (payload.role_id === 1) {
            this.router.navigate(['/admin-dashboard']);
          } 
          else {
            this.router.navigate(['/dashboard']);
          }
        });

        this.isLoading = false;
      },

      error: (err: any) => {
        console.error("Login Error:", err);

        // ✅ HANDLE 401 ERROR PROPERLY
        if (err.status === 401) {
          alert("Invalid Email or Password ❌");
        } else {
          alert("Server Error ⚠️ Try again later");
        }

        this.isLoading = false;
      }
    });
  }
}