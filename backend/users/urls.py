from django.urls import path
from .views import RegisterView, LoginView, LogoutView, CookieTokenRefreshView, ProfileView, Verify2FAView, TwoFactorToggleView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    # Tam adres: api/v1/auth/register/
    path('register/', RegisterView.as_view(), name='auth_register'),

    # Tam adres: api/v1/auth/login
    path('login/', LoginView.as_view(), name='auth_login'),
    path('login/2fa/verify/', Verify2FAView.as_view(), name='auth_verify_2fa'),

    path('logout/', LogoutView.as_view(), name='auth_logout'),

    path('login/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),

    path('request-password-reset/', PasswordResetRequestView.as_view(), name='request_password_reset'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/2fa/toggle/', TwoFactorToggleView.as_view(), name='profile_2fa_toggle'),
]