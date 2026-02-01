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

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    AuthVisualComponent,
    FormInputComponent,
    PrimaryButtonComponent,
  ],
  templateUrl: './forgot-password.component.html',
})
export class ForgotPasswordComponent {
  forgotPasswordForm: FormGroup;
  isLoading = false;
  successMessage: string | null = null;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private router: Router,
  ) {
    this.forgotPasswordForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
    });
  }

  get emailControl(): FormControl {
    return this.forgotPasswordForm.get('email') as FormControl;
  }

  onSubmit(): void {
    if (this.forgotPasswordForm.valid) {
      this.isLoading = true;
      this.errorMessage = null;
      this.successMessage = null;

      // API çağrısı simülasyonu
      setTimeout(() => {
        this.isLoading = false;
        // Güvenlik Prensibi: E-posta adresi mevcut olup olmadığına bakılmaksızın her zaman aynı başarı mesajını göster
        // Böylece e-posta numaralandırma saldırılarını önler.
        this.successMessage =
          'Eğer hesabınız varsa, parola sıfırlama bağlantısı e-posta adresinize gönderilmiştir.';
        this.forgotPasswordForm.reset();
      }, 1500);
    } else {
      this.forgotPasswordForm.markAllAsTouched();
    }
  }
}
