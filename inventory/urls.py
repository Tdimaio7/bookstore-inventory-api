from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

# Router de DRF para exponer /books y acciones personalizadas
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
]
