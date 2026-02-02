import { ApplicationConfig, provideBrowserGlobalErrorListeners, PLATFORM_ID } from '@angular/core';
import { provideRouter } from '@angular/router';
import {
  provideHttpClient,
  withInterceptors,
  withFetch,
  withXsrfConfiguration,
} from '@angular/common/http';
import { provideAppInitializer } from '@angular/core';
import { inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

import { routes } from './app.routes';
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { AuthService } from './core/auth/auth.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideClientHydration(withEventReplay()),

    // Django ile güvenli konuşmayı sağlayan yapı
    // Angular'ın "İnternete çıkış yapabilirsin" emridir, bu eklenmezse ApiService çalışmaz
    provideHttpClient(
      // "İnternete çıkarken her seferinde authInterceptor'a uğra" diyoruz, böylece her isteğe otomatik olarak o Django başlıkları ve cookie izinleri eklenecek
      withFetch(),
      withInterceptors([authInterceptor]), // Her istekte interceptor çalışsın
      withXsrfConfiguration({
        cookieName: 'csrftoken',
        headerName: 'X-CSRFToken',
      }),
    ),

    // Uygulama başlatılırken kimlik doğrulama kontrolü yap
    provideAppInitializer(() => {
      const authService = inject(AuthService);
      const platformId = inject(PLATFORM_ID);

      // Sadece tarayıcı ortamında (Client Side) auth kontrolü yap
      // Server Side (SSR) sırasında auth cookie'lere erişemeyiz ve gereksiz bekleme yaratırız
      if (isPlatformBrowser(platformId)) {
        return authService.checkAuth();
      }
      return; // Server tarafında hiçbir şey yapma
    }),
  ],
};
