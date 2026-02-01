import { Component, computed, inject, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import {
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
} from '@angular/forms';
import { AuthService } from '../../core/auth/auth.service';
import { PrimaryButtonComponent } from '../../shared/components/primary-button/primary-button.component';
import { FormInputComponent } from '../../shared/components/form-input/form-input.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, PrimaryButtonComponent, FormInputComponent],
  templateUrl: './profile.component.html',
})
export class ProfileComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  private fb = inject(FormBuilder);

  user = this.authService.currentUser;
  profileForm: FormGroup;
  isSaving = false;
  successMessage: string | null = null;

  // Formatlı isim gösterimi
  displayName = computed(() => {
    return this.user()?.full_name || 'Kullanıcı';
  });

  constructor() {
    this.profileForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      currentPassword: ['', [Validators.required]],
      newPassword: ['', [Validators.minLength(8)]],
      confirmNewPassword: [''],
    });

    // Kullanıcı bilgisi geldiğinde/değiştiğinde formu doldur
    effect(() => {
      const u = this.user();
      if (u) {
        this.profileForm.patchValue({
          email: u.email,
        });
      }
    });
  }

  get emailControl(): FormControl {
    return this.profileForm.get('email') as FormControl;
  }
  get currentPasswordControl(): FormControl {
    return this.profileForm.get('currentPassword') as FormControl;
  }
  get newPasswordControl(): FormControl {
    return this.profileForm.get('newPassword') as FormControl;
  }
  get confirmNewPasswordControl(): FormControl {
    return this.profileForm.get('confirmNewPassword') as FormControl;
  }

  onSave(): void {
    if (this.profileForm.valid) {
      this.isSaving = true;
      this.successMessage = null;

      // Backend Entegrasyonu
      this.authService.updateProfile(this.profileForm.value).subscribe({
        next: () => {
          this.isSaving = false;
          this.successMessage = 'Profil bilgileri başarıyla güncellendi.';

          // Formu temizle veya resetle (opsiyonel, parola alanlarını temizlemek iyi olur)
          this.profileForm.patchValue({
            currentPassword: '',
            newPassword: '',
            confirmNewPassword: '',
          });
          this.profileForm.markAsPristine();
          this.profileForm.markAsUntouched();

          setTimeout(() => (this.successMessage = null), 3000);
        },
        error: (err) => {
          this.isSaving = false;
          // Backend'den gelen hata mesajını göster
          // Genellikle err.error.detail içinde olur
          const errorMsg = err.error?.detail || 'Bir hata oluştu. Lütfen tekrar deneyiniz.';

          // Alert yerine daha şık bir yöntem kullanılabilir ama şimdilik alert
          alert(Array.isArray(errorMsg) ? errorMsg.join('\n') : errorMsg);
        },
      });
    } else {
      this.profileForm.markAllAsTouched();
    }
  }

  onLogout(): void {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/login']);
    });
  }
}
