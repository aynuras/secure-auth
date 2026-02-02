from django.contrib import admin
from django.urls import path, include
import os

urlpatterns = [
    # Admin URL'ini ortam değişkeninden, yoksa varsayılan 'admin/' olarak al
    path(os.getenv('ADMIN_URL', 'admin/'), admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
]
