from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PasswordHistory

User = get_user_model()

@receiver(post_save, sender=User)
def save_password_history(sender, instance, created, **kwargs):
    """
    Her parola (kullanıcı) kaydedildiğinde geçmişe ekle.
    Eğer parola aynı kalmışsa (hash değişmemişse) ekleme yapmayız.
    """
    # En son kaydedilen parolayı bul
    last_history = PasswordHistory.objects.filter(user=instance).first()
    
    # Eğer ilk kayıtsa veya parola hash'i son kayıttan farklıysa
    if created or (last_history and last_history.password_hash != instance.password):
        PasswordHistory.objects.create(
            user=instance, 
            password_hash=instance.password
        )
