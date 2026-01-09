from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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

        if extra_fields.get('is_staff'):
            raise ValueError('Superuser için is_staff=True olmalı.')
        if extra_fields.get('is_superuser'):
            raise ValueError('Superuser için is_superuser=True olmalı.')

        return self.create_user(email, password, **extra_fields)


# Veritabanındaki tabloyu temsil ve Django'nun AbstractUser sınıfından miras alır
class CustomUser(AbstractUser):
    username = None  # Username alanını devre dışı bırakıyoruz
    email = models.EmailField(unique=True, verbose_name='Email Adresi')

    USERNAME_FIELD = 'email'  # Giriş yaparken kimlik olarak email kullanılacak
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email