from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from .utils import log_audit

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name')


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True, min_length=3)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password')

    # Parola kurallarını burada doğrulatıyoruz
    def validate_password(self, value):
        try:
            validate_password(value)  # settings.py'deki kuralları çalıştırır
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        with transaction.atomic():
            # 1. Veri Temizliği - HTML escape backend tarafında veritabanına kaydederken yapılmamalı.
            # Output encoding (gösterirken temizleme) tercih edilmelidir.
            full_name = validated_data.pop('full_name').strip()

            # 2. İsim Parçalama
            name_parts = full_name.split(' ')
            first_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else name_parts[0]
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            # 3. Kayıt - Argon2 Hashing Manager içinde tetiklenir
            user = User.objects.create_user(
                email=validated_data['email'].lower(),
                password=validated_data['password'],
                first_name=first_name,
                last_name=last_name
            )
            return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Veritabanındaki parçalı ismi birleştirip 'full_name' olarak ekliyoruz
        representation['full_name'] = f"{instance.first_name} {instance.last_name}".strip()
        return representation

    def validate_full_name(self, value):
        if len(value.strip().split(' ')) < 2:
            raise serializers.ValidationError("Lütfen hem adınızı hem de soyadınızı giriniz.")
        return value


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    currentPassword = serializers.CharField(required=True, write_only=True)
    newPassword = serializers.CharField(required=False, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        current_password = attrs.get('currentPassword')

        # 1. Mevcut Parola Kontrolü
        if not user.check_password(current_password):
            log_audit(
                request=self.context['request'],
                user=user,
                action='UPDATE_PROFILE',
                is_success=False,
                details="Profil güncelleme hatası: Mevcut parola yanlış"
            )
            raise serializers.ValidationError({"currentPassword": "Mevcut parolanız hatalı."})

        return attrs

    def validate_email(self, value):
        user = self.context['request'].user
        if value != user.email:
            # E-Posta benzersiz mi?
            if User.objects.filter(email=value).exclude(id=user.id).exists():
                log_audit(
                    request=self.context['request'],
                    user=user,
                    action='UPDATE_PROFILE',
                    is_success=False,
                    details=f"E-Posta çakışması: {value}"
                )
                raise serializers.ValidationError("Bu e-posta adresi kullanılamaz.")
        return value

    def validate_newPassword(self, value):
        user = self.context['request'].user
        if value and len(value.strip()) > 0:
            try:
                validate_password(value, user=user)
            except DjangoValidationError as e:
                # String listesi error
                raise serializers.ValidationError(list(e.messages))
        return value

    def update(self, instance, validated_data):
        request = self.context['request']
        new_email = validated_data.get('email')
        new_password = validated_data.get('newPassword')

        # 2. E-Posta Değişikliği
        if new_email and new_email != instance.email:
            old_email = instance.email
            instance.email = new_email
            
            log_audit(
                request=request,
                user=instance,
                action='UPDATE_PROFILE',
                is_success=True,
                details=f"E-Posta değişti. Eski: {old_email} -> Yeni: {new_email}"
            )

        # 3. Parola Değişikliği
        if new_password and len(new_password.strip()) > 0:
            instance.set_password(new_password)
            
            log_audit(
                request=request,
                user=instance,
                action='PASSWORD_CHANGE',
                is_success=True,
                details="Kullanıcı parolasını değiştirdi."
            )

        instance.save()
        return instance