import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
} from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthVisualComponent } from '../../../shared/components/auth-visual/auth-visual.component';
import { FormInputComponent } from '../../../shared/components/form-input/form-input.component';
import { PrimaryButtonComponent } from '../../../shared/components/primary-button/primary-button.component';
import { GoogleButtonComponent } from '../../../shared/components/google-button/google-button.component';
import { AuthService } from '../../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    AuthVisualComponent,
    FormInputComponent,
    PrimaryButtonComponent,
    GoogleButtonComponent,
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  loginForm: FormGroup;
  isLoading = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });
  }

  get emailControl(): FormControl {
    return this.loginForm.get('email') as FormControl;
  }

  get passwordControl(): FormControl {
    return this.loginForm.get('password') as FormControl;
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;

      this.authService.login(this.loginForm.value).subscribe({
        next: () => {
          this.router.navigate(['/profile']);
        },
        error: (err) => {
          this.isLoading = false;
          // Hata mesajını backend'den gelen yapıya göre özelleştirebiliriz
          this.errorMessage = 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.';
        },
        complete: () => {
          this.isLoading = false;
        },
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }
}
