import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
/* Angular Material */
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-signup',
  standalone: true,
  templateUrl: './signup.html',
  styleUrls: ['./signup.css'],
  imports: [
    RouterModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatDialogModule
  ]
})
export class SignupComponent {

  signupForm: FormGroup;

  

  constructor(
  private fb: FormBuilder,
  private authService: AuthService,
  public dialogRef: MatDialogRef<SignupComponent>
) {
    this.signupForm = this.fb.group({
  full_name: ['', Validators.required],
  email: ['', [Validators.required, Validators.email]],
  password: ['', Validators.required],
  role_id: [1, Validators.required] // 1 = citizen
});
  }

  close() {
    this.dialogRef.close();
  }

onSubmit() {
  if (this.signupForm.valid) {

    this.authService.register(this.signupForm.value).subscribe({
      next: (res: any) => {
        console.log("Success:", res);
        alert("Registration Successful ✅");
        setTimeout(() => {
        this.dialogRef.close();
});
      },
      error: (err: any) => {
        console.error("Error:", err);
        alert("Registration Failed ❌");
      }
    });

  }
}
}