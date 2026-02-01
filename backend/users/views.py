from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .permissions import IsIpAllowed
from .serializers import RegisterSerializer, UserSerializer, UserUpdateSerializer
from .throttles import RegisterThrottle, LoginThrottle
from .models import AuditLog, IPBlacklist, IPWhitelist, UserSession
from .utils import get_client_ip, log_audit
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from datetime import timezone as dt_timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, AuthenticationFailed


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny, IsIpAllowed]
    throttle_classes = [RegisterThrottle]  # Saatte max 5 kayıt isteği

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Hassas verileri logdan temizle
            # Email dışındaki alanların içeriğini loglamamak en güvenlisidir.
            # Sadece hata mesajlarını logla, veriyi loglama.
            
            safe_email = request.data.get('email', 'N/A')
            
            # Başarısız kayıt denemesi logu
            log_audit(
                request=request,
                user=None,
                action='REGISTER',
                is_success=False,
                details=f"Email: {safe_email} | Kayıt Başarısız: Bu email zaten kullanılıyor olabilir."
            )
            # Güvenlik: Hata detaylarını saldırgana gösterme (User Enumeration önleme)
            return Response(
                {"detail": "Kayıt işlemi gerçekleştirilemedi. Lütfen bilgilerinizi kontrol ediniz."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Doğrulama başarılıysa standart create işlemine devam et
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # 1. Kullanıcıyı kaydet
        user = serializer.save()

        # 2. AuditLog: Kayıt İşlemi
        log_audit(
            request=self.request,
            user=user,
            action='REGISTER',
            is_success=True
        )


class LoginView(TokenObtainPairView):
    throttle_classes = [LoginThrottle]
    permission_classes = [IsIpAllowed]

    def post(self, request, *args, **kwargs):
        # Giriş denemesi yapılan email'i al
        email = request.data.get('email')
        password = request.data.get('password', '')
        
        # Kullanıcı varlığı kontrolü
        user = User.objects.filter(email=email).first()
        
        # Genel Hata Mesajı
        GENERIC_ERROR = {"detail": "Giriş bilgileri geçersiz."}

        # 2. Hesap Kilitleme Kontrolü
        if user and user.account_locked_until:
            if timezone.now() < user.account_locked_until:
                """TIMING ATTACK PREVENTION:
                Hesap kilitli olsa bile, saldırganın bunu yanıt süresinden anlamaması için şifre doğrulama işlemini "boşa" çalıştırıyoruz. 
                Bu sayede yanıt süresi kilitli olmayan bir hesapla aynı mertebede olur.
                """

                check_password(password, user.password)

                # Loglama yapıyoruz
                log_audit(
                    request=request,
                    user=user,
                    action='LOGIN',
                    is_success=False,
                    details=f"Hesap Kilitli Denemesi: {email}"
                )
                return Response(GENERIC_ERROR, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # Süre dolmuş, kilidi aç
                user.account_locked_until = None
                user.failed_login_attempts = 0
                user.save()

        try:
            """
            1. JWT Doğrulaması (SimpleJWT)
            super().post çağrısı SimpleJWT'nin TokenObtainPairView sınıfının post metodunu çalıştırır.
            Bu metod, gönderilen kimlik bilgilerini (e-posta ve parola) alır ve bunları doğrular.
            """
            response = super().post(request, *args, **kwargs)
        except (TokenError, InvalidToken, AuthenticationFailed):
            # Parola yanlışsa veya kullanıcı yoksa SimpleJWT hata fırlatır.
            # 500 hataları (Sistem hataları) burada yakalanmaz ve yukarı fırlatılır.
            response = Response({"detail": "Giriş başarısız"}, status=status.HTTP_401_UNAUTHORIZED)

        if response.status_code == 200:
            refresh_token = response.data.get('refresh')
            access_token = response.data.get('access')

            # Tokenları JSON yanıtından temizle
            if 'access' in response.data: del response.data['access']
            if 'refresh' in response.data: del response.data['refresh']

            response.data['message'] = "Giriş başarılı."
            
            if user:
                response.data['user'] = UserSerializer(user).data

            # Cookie Ayarları
            cookie_params = {
                'httponly': True,
                'secure': not settings.DEBUG,
                'samesite': 'Lax',
            }

            # Access Token
            if access_token:
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    max_age=3600,  # 1 saat
                    **cookie_params
                )

            # Refresh Token
            if refresh_token:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    max_age=7 * 24 * 3600,  # 7 gün
                    **cookie_params
                )

            # Audit Log & Session Creation
            if user:
                user.failed_login_attempts = 0
                user.account_locked_until = None
                user.save()

                log_audit(
                    request=request,
                    user=user,
                    action='LOGIN',
                    is_success=True
                )

                # --- SESSION OLUŞTURMA ---
                try:
                    # Token içeriğini çözümle (JTI ve Expire Date için)
                    token = RefreshToken(refresh_token)
                    jti = token['jti']
                    exp_timestamp = token['exp']
                    expires_at = datetime.fromtimestamp(exp_timestamp, tz=dt_timezone.utc)
                    
                    ip_addr = get_client_ip(request)

                    UserSession.objects.create(
                        user=user,
                        refresh_token=str(refresh_token),
                        jti=jti,
                        ip_address=ip_addr,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        expires_at=expires_at,
                        is_active=True
                    )
                except Exception as e:
                    # Session hatası kritik değil ama loglanmalı
                    log_audit(
                        request=request,
                        user=user,
                        action='LOGIN',
                        is_success=True, # Login başarılı ama session hatası
                        details=f"Session Oluşturma Hatası: {str(e)}"
                    )
        else:
            # --- GİRİŞ BAŞARISIZ (401) ---
            # response data'sı null olabilir, o yüzden yeniden oluşturuyoruz
            response = Response(GENERIC_ERROR, status=status.HTTP_401_UNAUTHORIZED)

            user_obj = user
            
            error_details = f"Email: {email}" if not user_obj else "Hatalı Şifre"

            # Başarısız giriş sayacı artır
            if user_obj:
                user_obj.failed_login_attempts += 1
                if user_obj.failed_login_attempts >= 5:
                    user_obj.account_locked_until = timezone.now() + timedelta(minutes=15) # 15 dakika kilitle
                    error_details += " - HESAP KİLİTLENDİ"
                user_obj.save()

            log_audit(
                request=request,
                user=user_obj,
                action='LOGIN',
                is_success=False,
                details=error_details
            )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # 1. Çerezden refresh token'ı oku
        refresh_token = request.COOKIES.get('refresh_token')

        # 2. Mutable data handling
        if refresh_token:
            if isinstance(request.data, dict):
                request.data['refresh'] = refresh_token
            elif hasattr(request.data, '_mutable'):
                request.data._mutable = True
                request.data['refresh'] = refresh_token
                request.data._mutable = False
            else:
                 pass

        response = super().post(request, *args, **kwargs)

        # 3. Eğer yeni bir access token üretildiyse (başarılıysa)
        if response.status_code == 200:
            access_token = response.data.get('access')

            # JSON'dan sil (Güvenlik)
            if 'access' in response.data:
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
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                jti = token['jti']
                token.blacklist()
                
                # Oturumu veritabanında da kapat (UserSession)
                UserSession.objects.filter(jti=jti).update(is_active=False)
        except Exception:
            pass

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

    def put(self, request):
        serializer = UserUpdateSerializer(
            instance=request.user, 
            data=request.data, 
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profil bilgileriniz başarıyla güncellendi."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)