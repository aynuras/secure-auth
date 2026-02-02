from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django settings modülünü belirle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Django settings dosyasındaki CELERY_ ile başlayan tüm ayarları al
app.config_from_object('django.conf:settings', namespace='CELERY')

# INSTALLED_APPS içindeki tasks.py dosyalarını otomatik bul
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
