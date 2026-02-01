import { inject, PLATFORM_ID } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../auth/auth.service';
import { map } from 'rxjs/operators';
import { isPlatformBrowser } from '@angular/common';
import { of } from 'rxjs';

export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const platformId = inject(PLATFORM_ID);

  // SSR (Sunucu) tarafında çalışıyorsak cookie olmadığı için kontrolü atlıyoruz
  // ve istemcinin (tarayıcının) karar vermesini bekliyoruz.
  if (!isPlatformBrowser(platformId)) {
    return true; // Sunucuda "geç" diyoruz, tarayıcıda tekrar kontrol edilecek
  }

  // 1. Durum: Kullanıcı hafızada (RAM) zaten varsa direkt geçir
  if (authService.isLoggedIn()) {
    return true;
  }

  // 2. Durum: Sayfa yenilenmiş, hafıza silinmiş olabilir. Backend'e sor.
  return authService.checkAuth().pipe(
    map((user) => {
      if (user) {
        return true; // Kullanıcı geldi, içeri al
      }
      // Kullanıcı yok veya hata aldı, Login'e yönlendir
      return router.createUrlTree(['/login']);
    }),
  );
};
