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
    two_factor_enabled = models.BooleanField(default=False, verbose_name="2FA Etkin mi?")
    
    # Hesap Kilitleme Alanları
    failed_login_attempts = models.IntegerField(default=0, verbose_name="Başarısız Giriş Denemeleri")
    account_locked_until = models.DateTimeField(null=True, blank=True, verbose_name="Hesap Kilitlenme Tarihi")

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
    details = models.TextField(null=True, blank=True, verbose_name="Detaylar/Hata Mesajı")

    class Meta:
        verbose_name = "Denetim Kaydı"
        verbose_name_plural = "Denetim Kayıtları"
        ordering = ['-created_at'] # En yeni log en üstte

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"


# Geçmiş Şifreler (Password History)
class PasswordHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_history'
    )
    password_hash = models.CharField(max_length=255, verbose_name="Şifre Özeti")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Geçmiş Şifre"
        verbose_name_plural = "Geçmiş Şifreler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.created_at}"


# Aktif Oturumlar / Refresh Tokenlar
class UserSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    refresh_token = models.TextField(verbose_name="Refresh Token")
    jti = models.CharField(max_length=255, unique=True, verbose_name="Token ID (JTI)")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name="Geçerlilik Bitiş")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "Kullanıcı Oturumu"
        verbose_name_plural = "Kullanıcı Oturumları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.ip_address} - {'Aktif' if self.is_active else 'Pasif'}"


# IP Kara Liste (Blacklist)
class IPBlacklist(models.Model):
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="IP Adresi")
    reason = models.TextField(null=True, blank=True, verbose_name="Engellenme Sebebi")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Engel Bitiş Tarihi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "IP Kara Liste"
        verbose_name_plural = "IP Kara Listesi"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ip_address} - {self.reason or 'Sebep belirtilmedi'}"


# IP Beyaz Liste (Whitelist)
class IPWhitelist(models.Model):
    ip_address = models.GenericIPAddressField(unique=True, verbose_name="IP Adresi")
    description = models.TextField(null=True, blank=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "IP Beyaz Liste"
        verbose_name_plural = "IP Beyaz Listesi"
        ordering = ['-created_at']

    def __str__(self):
        return self.ip_address
