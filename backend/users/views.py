from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .permissions import IsIpAllowed
from .serializers import RegisterSerializer, UserSerializer, UserUpdateSerializer, Verify2FASerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer, CustomTokenObtainPairSerializer
from .throttles import RegisterThrottle, LoginThrottle
from .models import UserSession
from .utils import get_client_ip, log_audit, generate_otp, send_otp_email, send_password_reset_email, COOKIE_PARAMS
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
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
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginThrottle]
    permission_classes = [IsIpAllowed]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password', '')
        user = User.objects.filter(email=email).first()
        GENERIC_ERROR = {"detail": "Giriş bilgileri geçersiz."}

        # 2. Hesap Kilitleme Kontrolü
        if user and user.account_locked_until:
            if timezone.now() < user.account_locked_until:
                check_password(password, user.password) # Timing attack prevention
                log_audit(request=request, user=user, action='LOGIN', is_success=False, details=f"Hesap Kilitli Denemesi: {email}")
                return Response(GENERIC_ERROR, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user.account_locked_until = None
                user.failed_login_attempts = 0
                user.save()

        # 3. Parola Kontrolü (SimpleJWT öncesi manuel kontrol -> 2FA için)
        if user and user.check_password(password):
            # --- 2FA KONTROLÜ ---
            if user.two_factor_enabled:
                otp_code = generate_otp()
                user.otp_code = otp_code
                user.otp_created_at = timezone.now()
                user.save()

                send_otp_email(user, otp_code)

                return Response({
                    "step": "2fa_required",
                    "email": user.email,
                    "message": "Doğrulama kodu e-posta adresinize gönderildi."
                }, status=status.HTTP_200_OK)

        # 4. Standart Login (SimpleJWT)
        try:
            response = super().post(request, *args, **kwargs)
        except Exception:
            # SimpleJWT veya Django auth hataları (Yanlış parola vb.)
            # Exception ne olursa olsun, bir response dönmeliyiz ki loglama akışı devam edebilsin.
            response = Response({"detail": "Giriş başarısız"}, status=status.HTTP_401_UNAUTHORIZED)

        if response.status_code == 200:
            # Login başarılı
            user = User.objects.get(email=email)
            refresh_token = response.data.get('refresh')
            access_token = response.data.get('access')

            if 'access' in response.data: del response.data['access']
            if 'refresh' in response.data: del response.data['refresh']

            response.data['message'] = "Giriş başarılı."
            response.data['user'] = UserSerializer(user).data

            if access_token: response.set_cookie(key='access_token', value=access_token, max_age=settings.JWT_ACCESS_COOKIE_AGE, **COOKIE_PARAMS)
            if refresh_token: response.set_cookie(key='refresh_token', value=refresh_token, max_age=settings.JWT_REFRESH_COOKIE_AGE, **COOKIE_PARAMS)

            if user:
                user.failed_login_attempts = 0
                user.account_locked_until = None
                user.save()
                log_audit(request=request, user=user, action='LOGIN', is_success=True)

                # Session creation
                token = RefreshToken(refresh_token)
                UserSession.objects.create(
                    user=user, 
                    refresh_token=str(refresh_token), 
                    jti=token['jti'],
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    expires_at=datetime.fromtimestamp(token['exp'], tz=dt_timezone.utc),
                    is_active=True
                )

        else:
            # Login Başarısız
            # Güvenlik notu: 'GENERIC_ERROR' kullanarak kullanıcının varlığını belli etmiyoruz
            # Ama backend tarafında loglama yapıyoruz.
            
            # Eğer response super().post()'tan exception yiyerek geldiyse, içeriği düzenle
            if response.status_code == 401:
                response = Response(GENERIC_ERROR, status=status.HTTP_401_UNAUTHORIZED)
            
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = timezone.now() + timedelta(minutes=15)
                user.save()
                log_audit(request=request, user=user, action='LOGIN', is_success=False, details="Hatalı Parola")
            else:
                 log_audit(request=request, user=None, action='LOGIN', is_success=False, details=f"Bilinmeyen Kullanıcı: {email}")

        return response


class Verify2FAView(APIView):
    permission_classes = [AllowAny, IsIpAllowed]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = Verify2FASerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "Geçersiz istek."}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp_code != code:
            user.failed_login_attempts += 1
            user.save()
            log_audit(request=request, user=user, action='LOGIN_2FA', is_success=False, details="Hatalı 2FA Kodu")
            return Response({"detail": "Hatalı kod."}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp_created_at and (timezone.now() - user.otp_created_at > timedelta(minutes=3)):
            log_audit(request=request, user=user, action='LOGIN_2FA', is_success=False, details="2FA Süresi Dolmuş")
            return Response({"detail": "Kodun süresi dolmuş. Lütfen tekrar giriş yapın."}, status=status.HTTP_400_BAD_REQUEST)

        # Success 2FA
        refresh = RefreshToken.for_user(user)
        # 2FA sonrası manuel oluşturulan token'a da JTI claim'ini ekle
        refresh['refresh_jti'] = refresh['jti']
        
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user.otp_code = None
        user.otp_created_at = None
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.save()

        response = Response({"message": "Giriş başarılı.", "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
        response.set_cookie(key='access_token', value=access_token, max_age=settings.JWT_ACCESS_COOKIE_AGE, **COOKIE_PARAMS)
        response.set_cookie(key='refresh_token', value=refresh_token, max_age=settings.JWT_REFRESH_COOKIE_AGE, **COOKIE_PARAMS)
        
        log_audit(request=request, user=user, action='LOGIN_2FA', is_success=True)

        # Refresh token içeriklerini çözümleyerek oturum oluştur
        refresh_obj = RefreshToken(refresh_token)
        
        UserSession.objects.create(
        user=user, 
        refresh_token=refresh_token, 
        jti=refresh_obj['jti'],
        ip_address=get_client_ip(request), 
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        expires_at=datetime.fromtimestamp(refresh_obj['exp'], tz=dt_timezone.utc), 
        is_active=True
        )

        return response


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle] # Limit koymak mantıklı

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Kullanıcı bulunamadıysa bile güvenlik gereği başarılı gibi davranıyoruz
                return Response({"message": "Parola sıfırlama bağlantısı e-posta adresinize gönderildi."}, status=status.HTTP_200_OK)

            # Link oluşturma
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Frontend URL'si (Angular'da routeları buna göre ayarlayacağız)
            # Örnek: http://localhost:4200/reset-password?uid=MQ&token=...
            reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

            if send_password_reset_email(user, reset_link):
                log_audit(
                    request=request,
                    user=user,
                    action='PASSWORD_RESET_REQUEST',
                    is_success=True,
                    details="Parola sıfırlama e-postası gönderildi."
                )
                return Response({"message": "Parola sıfırlama bağlantısı e-posta adresinize gönderildi."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "E-posta gönderilirken bir hata oluştu."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            log_audit(
                request=request,
                user=user,
                action='PASSWORD_RESET_CONFIRM',
                is_success=True,
                details="Parola başarıyla sıfırlandı."
            )
            return Response({"message": "Parolanız başarıyla sıfırlandı. Giriş yapabilirsiniz."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Toggle (Açıksa kapat, kapalıysa aç)
        user.two_factor_enabled = not user.two_factor_enabled
        user.save()
        
        status_text = "açıldı" if user.two_factor_enabled else "kapatıldı"
        log_audit(request=request, user=user, action='UPDATE_PROFILE', is_success=True, details=f"2FA {status_text}.")
        
        return Response({"message": f"2 Adımlı doğrulama {status_text}.", "two_factor_enabled": user.two_factor_enabled})


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny, IsIpAllowed]

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
            refresh_token = response.data.get('refresh')

            # JSON'dan sil (Güvenlik)
            if 'access' in response.data:
                del response.data['access']
            if 'refresh' in response.data:
                del response.data['refresh']

            # Yeni access token'ı tekrar güvenli çereze yaz
            response.set_cookie(
                key='access_token',
                value=access_token,
                max_age=settings.JWT_ACCESS_COOKIE_AGE,  # 1 saat
                **COOKIE_PARAMS
            )
            
            # Eğer refresh token rotasyonu açıksa yeni refresh token'ı da çereze yaz
            if refresh_token:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    max_age=settings.JWT_REFRESH_COOKIE_AGE, # 7 gün
                    **COOKIE_PARAMS
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
                session_id = token.get('refresh_jti', token['jti'])
                UserSession.objects.filter(jti=session_id).update(is_active=False)
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
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

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


class GenerateDiagnosticsTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        ip = get_client_ip(request)
        import uuid
        log_audit(
            request=request, 
            user=user, 
            action='SYSTEM_DIAGNOSTICS', 
            is_success=True, 
            details=f"POTENTIAL ATTACK DETECTED: User attempted to access hidden diagnostic endpoint. IP: {ip}"
        )
        fake_token = f"diag-{uuid.uuid4().hex[:8]}-pending-approval"
        return Response({
            "token": fake_token, 
            "status": "initiated", 
            "message": "Diagnostic token generated. Waiting for supervisor approval."
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)