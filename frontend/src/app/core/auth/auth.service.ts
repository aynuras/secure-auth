import { inject, Injectable, signal, computed } from '@angular/core';
import { ApiService } from '../services/api.service';
import { tap } from 'rxjs';

// Kullanıcı bilgilerinin tipi (Type Safety - Güvenlik için önemli)
export interface User {
  id: string; // UUID string olarak gelir
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string; // Django @property olarak tanımladığım alan
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
    return this.api.get<User>(`${this.AUTH_PATH}/profile/`).pipe(
      tap({
        next: (user) => this.currentUser.set(user),
        error: () => this.currentUser.set(null),
      }),
    );
  }

  // Giriş Yapma Fonksiyonu
  login(credentials: any) {
    return this.api.post<User>(`${this.AUTH_PATH}/login/`, credentials).pipe(
      // tap() operatörü: Veri geçerken araya girip sinyali günceller
      tap((user) => this.currentUser.set(user)),
    );
  }

  // Kayıt Olma Fonksiyonu
  register(userData: any) {
    return this.api.post<User>(`${this.AUTH_PATH}/register/`, userData);
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
