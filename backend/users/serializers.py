from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
import html

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True, min_length=3)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password')

    # Şifre kurallarını burada doğrulatıyoruz
    def validate_password(self, value):
        try:
            validate_password(value)  # settings.py'deki kuralları çalıştırır
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        with transaction.atomic():
            # 1. Veri Temizliği
            full_name = html.escape(validated_data.pop('full_name').strip())

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