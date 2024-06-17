import os
from django.core.wsgi import get_wsgi_application
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube_digest.settings')

application = get_wsgi_application()

def handler(environ, start_response):
    return application(environ, start_response)
