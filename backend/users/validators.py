from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .models import PasswordHistory

class MaximumPasswordHistoryValidator:
    def __init__(self, history_count=3):
        self.history_count = history_count

    def validate(self, password, user=None):
        if not user or not user.pk:
            return

        # Kullanıcının son parolalarını al
        last_passwords = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:self.history_count]
        
        for history in last_passwords:
            if check_password(password, history.password_hash):
                raise ValidationError(
                    f"Yeni parolanız son {self.history_count} parolanızdan biriyle aynı olamaz.",
                    code='password_history_reuse',
                )

    def get_help_text(self):
        return f"Parolanız son {self.history_count} parolanızdan farklı olmalıdır."
