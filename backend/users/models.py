from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
import uuid


# Tablo temsil etmez, veritabanına veri kaydedileceği zaman kuralları uygular
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email adresi zorunludur')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser için is_staff=True olmalı.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser için is_superuser=True olmalı.')

        return self.create_user(email, password, **extra_fields)


# Veritabanındaki tabloyu temsil ve Django'nun AbstractUser sınıfından miras alır
class CustomUser(AbstractUser):
    # Standart ID yerine UUID tanımlıyoruz
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    username = None  # Username alanını devre dışı bırakıyoruz
    email = models.EmailField(unique=True, verbose_name='Email Adresi')

    USERNAME_FIELD = 'email'  # Giriş yaparken kimlik olarak email kullanılacak
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def full_name(self):
        """Ad ve soyadı birleştirip tek bir string döner."""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.email


# Audit Log
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('REGISTER', 'Kayıt Olma'),
        ('LOGIN', 'Giriş Yapma'),
        ('LOGOUT', 'Çıkış Yapma'),
        ('PASSWORD_CHANGE', 'Şifre Değiştirme'),
    ]

    # user silinse bile logun kalması için SET_NULL kullandık
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True) # Tarayıcı/Cihaz bilgisi
    created_at = models.DateTimeField(auto_now_add=True)
    is_success = models.BooleanField(default=True, verbose_name="İşlem Başarılı mı?")

    class Meta:
        verbose_name = "Denetim Kaydı"
        verbose_name_plural = "Denetim Kayıtları"
        ordering = ['-created_at'] # En yeni log en üstte

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"