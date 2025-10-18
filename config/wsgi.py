import os
from django.core.wsgi import get_wsgi_application

# Punto de entrada WSGI para despliegues tradicionales
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
