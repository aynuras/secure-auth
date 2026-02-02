import logging
from ipware import get_client_ip as ipware_get_client_ip
from django.conf import settings

logger = logging.getLogger(__name__)

# Merkezi Çerez Ayarları
COOKIE_PARAMS = {
    'httponly': True,
    'secure': not settings.DEBUG,
    'samesite': 'Lax',
}

def get_client_ip(request):
    """
    Kullanıcının IP adresini tespit eder.
    django-ipware kütüphanesini kullanarak proxy arkası IP tespiti daha güvenli hale getirilmiştir.
    """
    client_ip, is_routable = ipware_get_client_ip(request)
    if client_ip is None:
        # IP tespit edilemezse fallback olarak REMOTE_ADDR dene
        return request.META.get('REMOTE_ADDR')
    return client_ip


def log_audit(request, action, user=None, is_success=True, details=None):
    """
    Merkezi Audit Log kayıt fonksiyonu.
    Hataları yutar ve konsola basar (akışı bozmamak için).
    """
    from .models import AuditLog
    
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        AuditLog.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            is_success=is_success,
            details=details
        )
    except Exception as e:
        # Loglama sistemi hatası (veritabanı erişilemez vb.)
        # Güvenlik gereği kullanıcıya hata göstermiyoruz ama sistem loglarına kaydediyoruz.
        logger.error(f"Audit Log Kaydedilemedi: {str(e)}")


def generate_otp():
    """6 haneli rastgele rakam üretir (Kriptografik olarak güvenli)."""
    import secrets
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


def send_otp_email(user, otp_code):
    """Kullanıcıya OTP kodunu mail atar."""
    from django.core.mail import send_mail
    from django.conf import settings

    subject = 'Güvenli Giriş Doğrulama Kodunuz'
    message = f"""Merhaba {user.first_name},

Hesabınıza giriş yapabilmek için doğrulama kodunuz: {otp_code}

Bu kod 3 dakika süreyle geçerlidir.
Eğer bu işlemi siz yapmadıysanız lütfen parolanızı değiştirin.
"""
    try:
        # Eğer Console Backend kullanılıyorsa (Demo/Dev ortamı)
        # Terminale temiz bir çıktı basıp fonksiyonu bitiriyoruz.
        # Böylece karmaşık MIME formatı ve encoding sorunlarından kurtuluyoruz.
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print(f"\n{'='*60}")
            print(f" DEMO E-POSTA SİMÜLASYONU")
            print(f" Kime: {user.email}")
            print(f" Konu: {subject}")
            print(f"{'-'*60}")
            print(message)
            print(f"{'='*60}\n")
            return True

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Mail Gönderme Hatası: {e}")
        return False


def send_password_reset_email(user, reset_link):
    """Kullanıcıya parola sıfırlama linkini mail atar."""
    from django.core.mail import send_mail
    from django.conf import settings

    subject = 'Parola Sıfırlama İsteği'
    message = f"""Merhaba {user.first_name},

Hesabınız için parola sıfırlama isteği aldık.
Parolanızı sıfırlamak için aşağıdaki bağlantıya tıklayın:

{reset_link}

Eğer bu isteği siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.
"""
    try:
        # Eğer Console Backend kullanılıyorsa (Demo/Dev ortamı) - Temiz çıktı
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            print(f"\n{'='*60}")
            print(f" DEMO E-POSTA SİMÜLASYONU")
            print(f" Kime: {user.email}")
            print(f" Konu: {subject}")
            print(f"{'-'*60}")
            print(message)
            print(f"{'='*60}\n")
            return True

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Mail Gönderme Hatası: {e}")
        return False

