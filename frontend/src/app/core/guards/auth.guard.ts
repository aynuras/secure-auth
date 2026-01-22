import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../auth/auth.service';
import { of } from 'rxjs';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // Eğer kullanıcı zaten signal'de varsa, direkt geçişe izin ver
  if (authService.currentUser()) {
    return true;
  }

  // Signal'den giriş durumunu kontrol et
  if (authService.isLoggedIn()) {
    return true; // Yol açık, geçebilir.
  }

  // Giriş yapmamış, Login sayfasına yönlendir.
  return router.parseUrl('/login');
};
