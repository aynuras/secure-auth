from django.urls import path
from .views import RegisterView, LoginView, LogoutView, CookieTokenRefreshView, ProfileView

urlpatterns = [
    # Tam adres: api/v1/auth/register/
    path('register/', RegisterView.as_view(), name='auth_register'),

    # Tam adres: api/v1/auth/login
    path('login/', LoginView.as_view(), name='auth_login'),

    path('logout/', LogoutView.as_view(), name='auth_logout'),

    # Tam adres: api/v1/auth/login/refresh/
    path('login/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', ProfileView.as_view(), name='profile'),
]