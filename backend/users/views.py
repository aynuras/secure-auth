from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from .throttles import RegisterThrottle
from .models import AuditLog
from .utils import get_client_ip
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle] # Bu view artık saatte sadece 5 isteğe izin verir

    # Bu metod, serializer.is_valid() doğrulamasından geçtikten sonra veritabanına kayıt yapılırken tetiklenir
    def perform_create(self, serializer):
        # 1. Kullanıcıyı oluştur ve değişkene ata
        user = serializer.save()

        # 2. AuditLog tablosuna kayıt at
        AuditLog.objects.create(
            user=user,
            action='REGISTER',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT')
        )

# repoya push'tan sonra
class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # 1. Standart JWT doğrulamasını yap (Email ve Şifre kontrolü)
        # Eğer bilgiler yanlışsa SimpleJWT otomatik olarak 401 hatası döner.
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            # 2. GÜVENLİK: Token'ları JSON içinden sil (Frontend görmesin)
            del response.data['access']
            del response.data['refresh']
            response.data['message'] = "Giriş başarılı."

            # 3. ACCESS TOKEN'I ÇEREZE YAZ (1 Saatlik)
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,  # JS erişemez (XSS Koruması)
                secure=not settings.DEBUG,  # Sadece HTTPS (Localde HTTP çalışır)
                samesite='Lax',  # CSRF koruması için
                max_age=3600  # 1 saat
            )

            # 4. REFRESH TOKEN'I ÇEREZE YAZ (7 Günlük)
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=7 * 24 * 3600  # 7 gün
            )

            # 5. AUDIT LOG: Kimin girdiğini UUID ile kaydet
            try:
                # Email üzerinden kullanıcıyı buluyoruz
                user_email = request.data.get('email')
                user = User.objects.get(email=user_email)

                AuditLog.objects.create(
                    user=user,  # UUID bazlı kullanıcı
                    action='LOGIN_SUCCESS',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except User.DoesNotExist:
                pass  # Teorik olarak buraya düşmemeli çünkü login başarılı oldu

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # 1. Çerezden refresh token'ı oku
        refresh_token = request.COOKIES.get('refresh_token')

        # 2. Eğer çerezde varsa, bunu sanki formdan gelmiş gibi veriye ekle
        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        # 3. Eğer yeni bir access token üretildiyse (başarılıysa)
        if response.status_code == 200:
            access_token = response.data.get('access')

            # JSON'dan sil (Güvenlik)
            del response.data['access']

            # Yeni access token'ı tekrar güvenli çereze yaz
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=3600  # 1 saat
            )
            response.data['message'] = "Token başarıyla tazelendi."

        return response


class LogoutView(APIView):
    # Sadece giriş yapmış olanlar çıkış yapabilir
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = Response({
            "message": "Başarıyla çıkış yapıldı. Çerezler temizlendi."
        }, status=200)

        # Tarayıcıdaki çerezleri siliyoruz
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        # Güvenlik için CSRF çerezini de temizlemek iyidir
        response.delete_cookie('csrftoken')

        return response


class ProfileView(APIView):
    permission_classes = [IsAuthenticated] # Sadece giriş yapanlar görebilir

    def get(self, request):
        return Response({
            "email": request.user.email,
            "full_name": request.user.full_name, # Modeldeki @property çalışacak
            "id": request.user.id
        })