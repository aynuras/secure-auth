from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AuditLog

# Kullanıcı Yönetimi
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    
    # Username olmadığı için fieldsets ayarlarını güncellememiz gerekir
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name')}),
        ('Yetkiler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password'),
        }),
    )


# Audit Log Yönetimi
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'ip_address', 'is_success', 'created_at']
    list_filter = ['action', 'is_success', 'created_at']
    search_fields = ['user__email', 'ip_address', 'user_agent']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    
    def has_add_permission(self, request):
        return False  # Loglar elle eklenememeli
