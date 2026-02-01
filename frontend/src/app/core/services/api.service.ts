import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private readonly baseUrl = environment.apiUrl;

  // Django'dan veri çekme metodu
  get<T>(path: string) {
    return this.http.get<T>(`${this.baseUrl}${path}`, { withCredentials: true });
  }

  // Django'ya veri gönderme metodu
  post<T>(path: string, body: any) {
    return this.http.post<T>(`${this.baseUrl}${path}`, body, { withCredentials: true });
  }

  // Veri güncelleme (Profil vb.)
  put<T>(path: string, body: any) {
    return this.http.put<T>(`${this.baseUrl}${path}`, body, { withCredentials: true });
  }
}

// Bu servis, Angular uygulamanızın Django backend ile iletişim kurmasını sağlar.

/*
- { withCredentials: true } ayarı, Django'nun gönderdiği HttpOnly Cookie (JWT) bilgilerinin tarayıcı tarafından her istekte otomatik olarak geri gönderilmesini sağlar. Bu, "Defense in Depth" stratejisinin ilk adımıdır. 
- Bu ayar sonucunda Angular token'ı görmez, okuyamaz ve değiştiremez. Sadece HttpOnly Cookie'de saklanan token'ı, Django'ya giderken otomatik olarak arkada taşır. Böylece Django, her istekte bu token'ı alır ve kullanır. 
- Bu, XSS saldırılarına karşı önemli bir koruma sağlar çünkü kötü niyetli bir JavaScript kodu bu token'a erişemez.
*/
