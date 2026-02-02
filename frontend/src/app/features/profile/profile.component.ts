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
import { ToggleSwitchComponent } from '../../shared/components/toggle-switch/toggle-switch.component';
import { ConfirmationModalComponent } from '../../shared/components/confirmation-modal/confirmation-modal.component';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    PrimaryButtonComponent,
    FormInputComponent,
    ToggleSwitchComponent,
    ConfirmationModalComponent,
  ],
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

  // Modal State
  isModalOpen = false;
  modalTitle = '';
  modalMessage = '';
  modalType: 'info' | 'success' | 'warning' | 'danger' = 'warning';
  pendingAction: (() => void) | null = null;

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

  onToggle2FA(): void {
    const isEnabled = this.user()?.two_factor_enabled;
    const action = isEnabled ? 'kapatmak' : 'açmak';

    this.modalTitle = isEnabled ? '2FA Kapatılsın mı?' : '2FA Açılsın mı?';
    this.modalMessage = `Hesabınız için 2 adımlı doğrulamayı ${action} üzeresiniz. Bu işlem güvenliğinizi etkileyecektir.`;
    this.modalType = isEnabled ? 'danger' : 'success';

    this.pendingAction = () => {
      this.authService.toggle2FA().subscribe({
        next: () => {
          // Başarılı olduğunda modalı kapat, kullanıcı zaten güncellendi (signal)
          this.closeModal();
        },
        error: () => {
          this.closeModal();
          alert('İşlem sırasında bir hata oluştu.');
        },
      });
    };

    this.isModalOpen = true;
  }

  confirmModal() {
    if (this.pendingAction) {
      this.pendingAction();
    }
  }

  closeModal() {
    this.isModalOpen = false;
    this.pendingAction = null;
  }

  onLogout(): void {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/login']);
    });
  }
}
