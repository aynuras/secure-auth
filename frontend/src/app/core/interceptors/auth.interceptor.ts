import { HttpInterceptorFn } from '@angular/common/http';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  // İsteği klonlayıp (orijinal veri bozulmasın diye) içine güvenlik başlıkları ekliyoruz
  const secureReq = req.clone({
    setHeaders: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest', // Django'nun AJAX isteği olduğunu anlaması için
    },
    withCredentials: true, // Cookie'leri her zaman dahil et
  });

  return next(secureReq);
};

/*
- Uygulamanın 20 farklı yerinden Django'ya (API) istek atıyorsun. Her seferinde "Merhaba, ben güvenliyim, işte kimliğim, işte paketim" demek çok yorucu.
- Sen sadece paketi (veriyi) hazırlıyorsun. Interceptor, paket kapıdan çıkmadan hemen önce onu yakalıyor, üzerine "Güvenli Gönderi" damgasını basıyor, içine Django'nun istediği özel belgeleri (CSRF, Cookie izinleri) yerleştiriyor ve öyle gönderiyor.
- Böylece Django, paketi aldığında "Bu adam güvenilir, içeri alabiliriz" diyor ve veriyi kabul ediyor.
- Bu, uygulamanın her yerinde güvenli istekler atılmasını sağlar ve kod tekrarını önler.
*/
