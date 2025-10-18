from django.contrib import admin
from django.urls import path, include

# Rutas del proyecto: admin y API de la app inventory
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),  # expone /books y acciones asociadas
]
