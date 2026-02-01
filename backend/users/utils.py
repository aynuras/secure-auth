import logging
from ipware import get_client_ip as ipware_get_client_ip

logger = logging.getLogger(__name__)

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

