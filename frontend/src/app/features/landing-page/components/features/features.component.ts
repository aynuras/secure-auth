import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PageHeaderComponent } from '../../../../shared/components/page-header/page-header.component';
import { FeatureCardComponent } from '../../../../shared/components/feature-card/feature-card.component';

interface Feature {
  title: string;
  subtitle: string;
  description: string;
  iconName: string;
}

@Component({
  selector: 'app-features',
  standalone: true,
  imports: [CommonModule, PageHeaderComponent, FeatureCardComponent],
  templateUrl: './features.component.html',
})
export class FeaturesComponent {
  features: Feature[] = [
    {
      title: 'Secure Token Storage',
      subtitle: 'JWT via HttpOnly Cookies',
      description:
        "Token'ların JavaScript tarafından okunmasını engelleyerek token maruziyetini azaltır.",
      iconName: 'vpn_key',
    },
    {
      title: 'Refresh Token Rotation',
      subtitle: 'Secure Session Management',
      description:
        "Refresh Token'lar yenilendiğinde rotate edilir ve JTI takibi ile aktif oturumlar gerektiğinde geçersiz kılınabilir.",
      iconName: 'autorenew',
    },
    {
      title: 'Input Validation',
      subtitle: 'Client & Server-Side Validation',
      description:
        'İstemci ve sunucu tarafında gelen verilerin beklenen format ve kurallara uygunluğu kontrol edilir.',
      iconName: 'verified_user',
    },
    {
      title: 'Audit Logging',
      subtitle: 'Automated Event Logging',
      description:
        'Login, registration ve parola değişikliği gibi kritik işlemler güvenlik denetimi için kayıt altına alınır.',
      iconName: 'history_edu',
    },
    {
      title: 'Brute Force Protection',
      subtitle: 'Rate Limiting & Account Lockout',
      description:
        'Tekrarlanan başarısız girişler sınırlandırılır ve belirli denemeler sonrasında hesap kilitleme uygulanır.',
      iconName: 'shield',
    },
    {
      title: 'CSRF & CORS Protection',
      subtitle: 'Controlled Cross-Origin Access',
      description:
        'Cross-origin istekler sınırlandırılır ve authentication akışlarında CSRF riskini azaltmaya yönelik kontroller uygulanır.',
      iconName: 'fingerprint',
    },
  ];
}
