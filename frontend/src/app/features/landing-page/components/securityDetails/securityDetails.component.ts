import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PageHeaderComponent } from '../../../../shared/components/page-header/page-header.component';

interface SecurityTab {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  details: string;
  backendCodeTitle: string;
  backendCode: string;
  frontendCodeTitle: string;
  frontendCode: string;
}

@Component({
  selector: 'app-securityDetails',
  standalone: true,
  imports: [CommonModule, PageHeaderComponent],
  templateUrl: './securityDetails.component.html',
})
export class SecurityDetailsComponent {
  activeTabId = 'storage';

  tabs: SecurityTab[] = [
    {
      id: 'storage',
      title: 'Secure Storage',
      subtitle: 'HttpOnly Cookies',
      description: 'Token Güvenliği ve XSS Koruması',
      details:
        "JWT token'ları localStorage yerine HttpOnly Cookie'lerde saklanarak JavaScript saldırılarına (XSS) karşı tam koruma sağlanır.",
      backendCodeTitle: 'users/views.py',
      backendCode: `response.set_cookie(
    key='access_token',
    value=access_token,
    httponly=True,  # JS cannot read this
    secure=True,    # HTTPS only
    samesite='Lax'  # CSRF protection
)`,
      frontendCodeTitle: 'core/services/api.service.ts',
      frontendCode: `get<T>(path: string, options: { headers?: any } = {}) {
  return this.http.get<T>(\`\${this.baseUrl}\${path}\`, {
    withCredentials: true,
    headers: options.headers,
  });
}`,
    },
    {
      id: 'transport',
      title: 'Communication',
      subtitle: 'CORS & Interceptors',
      description: 'Güvenli İletişim Protokolü',
      details:
        'Frontend ve Backend arasındaki iletişim, sıkı CORS politikaları ve otomatik güvenlik başlıkları ile şifrelenir ve doğrulanır.',
      backendCodeTitle: 'core/settings.py',
      backendCode: `CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:4200').split(',')
CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'`,
      frontendCodeTitle: 'core/interceptors/auth.interceptor.ts',
      frontendCode: `const secureReq = req.clone({
  setHeaders: {
    Accept: 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  withCredentials: true
});`,
    },
    {
      id: 'access',
      title: 'Access Control',
      subtitle: 'Guards & Permissions',
      description: 'Çift Katmanlı Yetkilendirme',
      details:
        "Frontend'de Route Guard'lar ile sayfa geçişleri kontrol edilirken, Backend'de DRF Permission sınıfları ile veri güvenliği sağlanır.",
      backendCodeTitle: 'users/views.py',
      backendCode: `class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)`,
      frontendCodeTitle: 'core/guards/auth.guard.ts',
      frontendCode: `if (authService.isLoggedIn()) {
  return true;
}

return authService.checkAuth().pipe(
  map((user) => {
    return user ? true : router.createUrlTree(['/login']);
  })
);`,
    },
  ];

  get activeTab() {
    return this.tabs.find((t) => t.id === this.activeTabId) || this.tabs[0];
  }

  setActiveTab(id: string) {
    this.activeTabId = id;
  }
}
