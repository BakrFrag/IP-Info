import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ip_info.settings')
app = Celery('ip_info')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
