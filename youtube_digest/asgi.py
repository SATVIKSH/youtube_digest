"""
ASGI config for youtube_digest project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""



from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter

from django.urls import path



application = get_asgi_application()