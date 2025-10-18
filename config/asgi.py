import os
from django.core.asgi import get_asgi_application

# Punto de entrada ASGI para servidores asíncronos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
