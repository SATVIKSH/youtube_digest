from __future__ import absolute_import,unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE','youtube_digest.settings')

app=Celery('youtube_digest',backend='redis://default:mWHmnhnuUVKzsvqzJRPwIUwRMdIptESX@roundhouse.proxy.rlwy.net:25177',
             broker='redis://default:mWHmnhnuUVKzsvqzJRPwIUwRMdIptESX@roundhouse.proxy.rlwy.net:25177')


app.config_from_object(settings,namespace='CELERY')

app.autodiscover_tasks(lambda:settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')