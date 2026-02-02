import { inject, Injectable, signal, computed } from '@angular/core';
import { ApiService } from '../services/api.service';
import { tap, catchError, of, switchMap, delay } from 'rxjs';

// Kullanıcı bilgilerinin tipi (Type Safety - Güvenlik için önemli)
export interface User {
  id: string; // UUID string olarak gelir
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string; // Django @property olarak tanımladığım alan
  two_factor_enabled?: boolean; // 2FA Durumu
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private api = inject(ApiService);

  // Endpoint prefix'i - Django'daki yapıya göre
  private readonly AUTH_PATH = 'api/v1/auth';

  // 1.Signal: Kullanıcı bilgisini saklayan "Reaktif Değişken"
  // null ise kimse giriş yapmamış demektir
  currentUser = signal<User | null>(null);

  // 2.Computed Signal: Giriş yapılıp yapılmadığını otomatik hesaplar
  // Bu, dışarıdan değiştirilemez, sadece izlenebilir (Read-only)
  isLoggedIn = computed(() => !!this.currentUser());

  // Kimlik Doğrulama Kontrol Fonksiyonu
  checkAuth() {
    // X-Silent-Auth: 401 hatası alırsa interceptor'ın kullanıcıyı login sayfasına yönlendirmesini engeller.
    // Bu sayede Landing Page'i ziyaret eden kayıtsız kullanıcılar login sayfasına düşmez.
    return this.api
      .get<User>(`${this.AUTH_PATH}/profile/`, { headers: { 'X-Silent-Auth': 'true' } })
      .pipe(
        tap((user) => this.currentUser.set(user)), // Başarılı olursa kullanıcıyı set et
        catchError(() => {
          this.currentUser.set(null); // Hata olursa (401 vb.) kullanıcıyı null yap
          return of(null); // Hatayı yut ve akışın bozulmadan devam etmesini sağla
        }),
      );
  }

  // Giriş Yapma Fonksiyonu
  login(credentials: any) {
    // Backend artık user objesini dönüyor, tekrar istek atmaya gerek yok.
    return this.api.post<any>(`${this.AUTH_PATH}/login/`, credentials).pipe(
      tap((response) => {
        if (response.user) {
          this.currentUser.set(response.user);
        }
      }),
    );
  }

  // 2FA Doğrulama Fonksiyonu
  verify2FA(data: { email: string; code: string }) {
    return this.api.post<any>(`${this.AUTH_PATH}/login/2fa/verify/`, data).pipe(
      tap((response) => {
        if (response.user) {
          this.currentUser.set(response.user);
        }
      }),
    );
  }

  // 2FA Açma/Kapama (Toggle)
  toggle2FA() {
    return this.api.post<any>(`${this.AUTH_PATH}/profile/2fa/toggle/`, {}).pipe(
      tap(() => {
        // Veritabanı gecikmesini önlemek için (Optimistic Update)
        // Tekrar istek atmak yerine elimizdeki veriyi güncelliyoruz.
        const current = this.currentUser();
        if (current) {
          const updatedUser = {
            ...current,
            two_factor_enabled: !current.two_factor_enabled,
          };
          this.currentUser.set(updatedUser);
        }
      }),
    );
  }

  // Kayıt Olma Fonksiyonu
  register(userData: any) {
    return this.api.post<User>(`${this.AUTH_PATH}/register/`, userData);
  }

  // Profil Güncelleme Fonksiyonu
  updateProfile(data: any) {
    // Profil güncellendikten sonra, en güncel hali için tekrar checkAuth yapıyoruz
    return this.api.put(`${this.AUTH_PATH}/profile/`, data).pipe(
      delay(100),
      switchMap(() => this.checkAuth()),
    );
  }

  // Token Yenileme Fonksiyonu
  refreshToken() {
    return this.api.post<any>(`${this.AUTH_PATH}/login/refresh/`, {}).pipe(
      tap(() => {
        // Token yenileme başarılıysa (httpOnly cookie güncellenir)
        // İsteğe bağlı: Kullanıcı bilgisini tekrar çekebiliriz veya sadece devam ederiz
        // Biz burada sessizce devam ediyoruz.
      }),
    );
  }

  requestPasswordReset(email: string) {
    return this.api.post(`${this.AUTH_PATH}/request-password-reset/`, { email });
  }

  confirmPasswordReset(data: any) {
    return this.api.post(`${this.AUTH_PATH}/reset-password/`, data);
  }

  // Çıkış Yapma Fonksiyonu
  logout() {
    return this.api
      .post(`${this.AUTH_PATH}/logout/`, {})
      .pipe(tap(() => this.currentUser.set(null)));
  }
}

/*
UUID Kullanımı: Saldırganlar /api/users/1, /api/users/2 gibi tahmin edilebilir ID'lerle veri çekmeye çalışamazlar. Angular tarafında da id: string diyerek bu karmaşık yapıyı destekliyoruz.

No Username: username saldırganların keşif aşamasında en çok kullandığı bilgidir. Biz sadece email kullanarak "Attack Surface"i yani saldırı yüzeyini daralttık.

Property Mapping: Django'daki @property def full_name kullanımı veritabanında yer kaplamıyor ama frontend'e temiz bir isim-soyisim paketi sunuyor.
*/
