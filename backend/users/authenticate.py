from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import UserSession


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Önce Header'a bak, orada yoksa Cookie'den al
        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get('access_token')
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # 1. Kullanıcı aktiflik kontrolü (Admin banlarsa anında erişim kesilir)
        if not user.is_active:
            raise AuthenticationFailed("Hesabınız devre dışı bırakılmıştır.", code="user_inactive")

        # 2. Session kontrolü (Logout yaparsa veya session silinirse erişim kesilir)
        # Sadece "herhangi bir oturum" değil, "BU oturum" aktif mi diye bakıyoruz.
        refresh_jti = validated_token.get('refresh_jti')
        
        session_query = UserSession.objects.filter(user=user, is_active=True)
        
        # Eğer token 'refresh_jti' claim'ine sahipse, nokta atışı kontrol yap.
        # (Eski tokenlar için geriye dönük uyumluluk isteniyorsa else bloğu eklenebilir ama güvenli olan budur)
        if refresh_jti:
            session_query = session_query.filter(jti=refresh_jti)
            
        if not session_query.exists():
            raise AuthenticationFailed("Oturumunuz sonlanmış veya geçersiz.", code="session_invalid")

        return user, validated_token