from celery import shared_task
from django.utils import timezone
from .models import AuditLog
from datetime import timedelta

@shared_task
def clear_old_audit_logs():
    """
    90 günden eski Audit Log kayıtlarını veritabanından siler.
    Bu işlem veritabanı boyutunu kontrol altında tutmak için periyodik olarak çalıştırılmalıdır.
    """
    retention_period = timezone.now() - timedelta(days=90)
    deleted_count, _ = AuditLog.objects.filter(created_at__lt=retention_period).delete()
    
    return f"{deleted_count} adet eski audit log kaydı silindi."
