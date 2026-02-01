from rest_framework import permissions
from .models import IPBlacklist, IPWhitelist
from .utils import get_client_ip

# IP Bloklama ve İzin Verme listesine göre erişimi kontrol eder.
class IsIpAllowed(permissions.BasePermission):
    message = "IP Adresiniz engellendi."

    def has_permission(self, request, view):
        ip_addr = get_client_ip(request)
        
        # Eğer IP blacklistte varsa ve Whitelistte YOKSA engelle
        if IPBlacklist.objects.filter(ip_address=ip_addr, is_active=True).exists():
            if not IPWhitelist.objects.filter(ip_address=ip_addr, is_active=True).exists():
                return False
        
        return True
