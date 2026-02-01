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
  selector: 'app-register',
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
  templateUrl: './register.component.html',
})
export class RegisterComponent {
  registerForm: FormGroup;
  isLoading = false;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
  ) {
    this.registerForm = this.fb.group({
      fullName: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
    });
  }

  get fullNameControl(): FormControl {
    return this.registerForm.get('fullName') as FormControl;
  }

  get emailControl(): FormControl {
    return this.registerForm.get('email') as FormControl;
  }

  get passwordControl(): FormControl {
    return this.registerForm.get('password') as FormControl;
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;

      const { fullName, email, password } = this.registerForm.value;

      const userData = {
        full_name: fullName,
        email: email,
        password: password,
      };

      this.authService.register(userData).subscribe({
        next: () => {
          this.router.navigate(['/login']);
        },
        error: (err) => {
          this.isLoading = false;
          // Güvenlik Önlemi: Backend'den gelen ham hatayı kullanıcıya göstermek yerine kontrol ederek veya genel bir mesajla gösteriyoruz.
          if (err.status === 400 && err.error) {
            // Sadece 400 Bad Request (Validation) hatalarında detay gösteriyoruz
            const values = Object.values(err.error);
            if (values.length > 0) {
              const firstError = Array.isArray(values[0]) ? values[0][0] : values[0];
              this.errorMessage = String(firstError);
            } else {
              this.errorMessage = 'Girdiğiniz bilgileri kontrol ediniz.';
            }
          } else {
            // 500 vb. sunucu hatalarında detay gizlenir
            this.errorMessage =
              'Kayıt işlemi sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.';
          }
        },
        complete: () => {
          this.isLoading = false;
        },
      });
    } else {
      this.registerForm.markAllAsTouched();
    }
  }
}
