import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
// Material
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import {RouterModule } from '@angular/router';

@Component({
  selector: 'app-police-signup',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    RouterModule
  ],
  templateUrl: './police-signup.html',
  styleUrls: ['./police-signup.css']
})
export class PoliceSignupComponent implements OnInit {

  signupForm!: FormGroup;

  constructor(private fb: FormBuilder, private auth: AuthService) {}

  ngOnInit() {
    this.signupForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      mobile: ['', [
        Validators.required,
        Validators.pattern('^[0-9]{10}$')
      ]],
      station_name: ['', Validators.required],
      role: ['Police'] // default role
    });
  }

  // ✅ Submit form
onSubmit() {
  console.log("Button clicked"); 
  if (this.signupForm.invalid) {
    alert("Please fill all fields correctly");
    return;
  }

this.auth.policeSignup(this.signupForm.value).subscribe({
  next: (res: any) => {
    console.log("SUCCESS", res);  // 👈 ADD
    alert(res.message || "Registered Successfully");
  },
  error: (err) => {
    console.log("ERROR", err);   // 👈 ADD
    alert("Registration Failed");
  }
});
}

  // ❌ Close popup
  close() {
    window.history.back();
  }
}