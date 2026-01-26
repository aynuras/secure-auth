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
  styleUrls: ['./features.component.css'],
})
export class FeaturesComponent {
  features: Feature[] = [
    {
      title: 'Secure Token Storage',
      subtitle: 'JWT via HttpOnly Cookies',
      description: "XSS saldırılarını önler; script'ler token'ı okuyamaz.",
      iconName: 'vpn_key',
    },
    {
      title: 'Resilient Auth Flow',
      subtitle: 'Silent Refresh Mechanism',
      description:
        "Kullanıcı deneyimini bozmadan, kısa ömürlü Access Token'lar ile güvenliği maksimize eder.",
      iconName: 'autorenew',
    },
    {
      title: 'Data Integrity',
      subtitle: 'Zod/Django Serializer Validation',
      description: 'Hem Client hem Server tarafında "Zero Trust" veri doğrulaması.',
      iconName: 'verified_user',
    },
    {
      title: 'Audit & Compliance',
      subtitle: 'Automated Event Logging',
      description:
        'Her kritik işlem (giriş, şifre değişimi, hata) Django Signal ile izlenir ve loglanır.',
      iconName: 'history_edu',
    },
    {
      title: 'Brute Force Protection',
      subtitle: 'Account Lockout Policy',
      description:
        'Ardışık hatalı girişlerde hesabı dondurarak kaba kuvvet saldırılarını engeller.',
      iconName: 'shield',
    },
    {
      title: 'Session Isolation',
      subtitle: 'Strict CORS & CSRF Protection',
      description: 'Sadece izinli kökenlerden gelen talepleri kabul eden katı köken kontrolü.',
      iconName: 'fingerprint',
    },
  ];
}
