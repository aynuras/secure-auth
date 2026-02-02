import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
} from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AuthVisualComponent } from '../../../shared/components/auth-visual/auth-visual.component';
import { FormInputComponent } from '../../../shared/components/form-input/form-input.component';
import { PrimaryButtonComponent } from '../../../shared/components/primary-button/primary-button.component';
import { AuthService } from '../../../core/auth/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    AuthVisualComponent,
    FormInputComponent,
    PrimaryButtonComponent,
  ],
  templateUrl: './reset-password.component.html',
})
export class ResetPasswordComponent implements OnInit {
  resetPasswordForm: FormGroup;
  isLoading = false;
  successMessage: string | null = null;
  errorMessage: string | null = null;
  uid: string | null = null;
  token: string | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService,
  ) {
    this.resetPasswordForm = this.fb.group(
      {
        password: ['', [Validators.required, Validators.minLength(8)]],
        confirmPassword: ['', [Validators.required]],
      },
      { validators: this.passwordMatchValidator },
    );
  }

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      this.uid = params['uid'];
      this.token = params['token'];

      if (!this.uid || !this.token) {
        this.errorMessage = 'Geçersiz veya eksik bağlantı.';
      }
    });
  }

  passwordMatchValidator(g: FormGroup) {
    return g.get('password')?.value === g.get('confirmPassword')?.value ? null : { mismatch: true };
  }

  get passwordControl(): FormControl {
    return this.resetPasswordForm.get('password') as FormControl;
  }

  get confirmPasswordControl(): FormControl {
    return this.resetPasswordForm.get('confirmPassword') as FormControl;
  }

  onSubmit(): void {
    if (this.resetPasswordForm.valid && this.uid && this.token) {
      this.isLoading = true;
      this.errorMessage = null;
      this.successMessage = null;

      const data = {
        uid: this.uid,
        token: this.token,
        password: this.resetPasswordForm.value.password,
      };

      this.authService.confirmPasswordReset(data).subscribe({
        next: (response: any) => {
          this.isLoading = false;
          this.successMessage =
            response.message ||
            'Parolanız başarıyla sıfırlandı. Giriş sayfasına yönlendiriliyorsunuz...';
          this.resetPasswordForm.reset();

          setTimeout(() => {
            this.router.navigate(['/login']);
          }, 3000);
        },
        error: (err: any) => {
          this.isLoading = false;
          this.errorMessage =
            err.error?.token ||
            'Parola sıfırlama işlemi başarısız. Bağlantı süresi dolmuş olabilir.';
        },
      });
    } else {
      this.resetPasswordForm.markAllAsTouched();
    }
  }
}
