import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../auth/auth.service';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  // İsteği klonlayıp (orijinal veri bozulmasın diye) içine güvenlik başlıkları ekliyoruz
  const secureReq = req.clone({
    setHeaders: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest', // Django'nun AJAX isteği olduğunu anlaması için
    },
    withCredentials: true, // Cookie'leri her zaman dahil et
  });

  return next(secureReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Eğer 401 hatası aldıysak ve bu istek zaten refresh isteği veya login isteği değilse
      // Login isteği başarısız olduğunda refresh denememeliyiz, direkt hata dönmeliyiz.
      if (
        error.status === 401 &&
        !req.url.includes('login/refresh') &&
        !req.url.includes('auth/login')
      ) {
        return authService.refreshToken().pipe(
          switchMap(() => {
            // Token yenilendi, orijinal isteği tekrarla
            return next(secureReq);
          }),
          catchError((refreshError) => {
            // Refresh de başarısız oldu (Session tamamen bitti) veya refresh token geçersiz

            // Client tarafında çıkış yap (Backend'e ulaşamasak bile)
            authService.currentUser.set(null);

            router.navigate(['/login']);
            return throwError(() => refreshError);
          }),
        );
      }
      return throwError(() => error);
    }),
  );
};

/*
- Uygulamanın 20 farklı yerinden Django'ya (API) istek atıyorsun. Her seferinde "Merhaba, ben güvenliyim, işte kimliğim, işte paketim" demek çok yorucu.
- Sen sadece paketi (veriyi) hazırlıyorsun. Interceptor, paket kapıdan çıkmadan hemen önce onu yakalıyor, üzerine "Güvenli Gönderi" damgasını basıyor, içine Django'nun istediği özel belgeleri (CSRF, Cookie izinleri) yerleştiriyor ve öyle gönderiyor.
- Böylece Django, paketi aldığında "Bu adam güvenilir, içeri alabiliriz" diyor ve veriyi kabul ediyor.
- Bu, uygulamanın her yerinde güvenli istekler atılmasını sağlar ve kod tekrarını önler.
*/
