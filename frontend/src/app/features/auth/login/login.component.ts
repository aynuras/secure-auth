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
  verifyForm: FormGroup; // 2FA Formu
  isLoading = false;
  errorMessage: string | null = null;

  // 2FA State Management
  step: 'login' | '2fa' = 'login';
  tempEmail: string = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });

    this.verifyForm = this.fb.group({
      code: ['', [Validators.required, Validators.minLength(6), Validators.maxLength(6)]],
    });
  }

  get emailControl(): FormControl {
    return this.loginForm.get('email') as FormControl;
  }

  get passwordControl(): FormControl {
    return this.loginForm.get('password') as FormControl;
  }

  get codeControl(): FormControl {
    return this.verifyForm.get('code') as FormControl;
  }

  onSubmit(): void {
    if (this.loginForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;

      this.authService.login(this.loginForm.value).subscribe({
        next: (response: any) => {
          // response tipi any olarak açık bırakıldı
          this.isLoading = false;

          if (response.step === '2fa_required') {
            this.step = '2fa';
            this.tempEmail = response.email;
            this.errorMessage = null;
          } else {
            this.router.navigate(['/profile']);
          }
        },
        error: (err) => {
          this.isLoading = false;
          // Hata mesajını backend'den gelen yapıya göre özelleştirebiliriz
          this.errorMessage = 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.';
        },
        complete: () => {
          // Loading login adımında kapandı.
        },
      });
    } else {
      this.loginForm.markAllAsTouched();
    }
  }

  onVerifySubmit(): void {
    if (this.verifyForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;

      const data = {
        email: this.tempEmail,
        code: this.verifyForm.value.code,
      };

      this.authService.verify2FA(data).subscribe({
        next: () => {
          this.router.navigate(['/profile']);
        },
        error: (err) => {
          this.isLoading = false;
          this.errorMessage = err.error?.detail || 'Kod doğrulanamadı.';
        },
        complete: () => {
          this.isLoading = false;
        },
      });
    } else {
      this.verifyForm.markAllAsTouched();
    }
  }
}
