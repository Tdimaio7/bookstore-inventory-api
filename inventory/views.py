from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import requests

from .models import Book
from .serializers import BookSerializer

EXCHANGE_API_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

def _quantize(value: Decimal) -> Decimal:
    # Redondeo financiero a 2 decimales
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def get_exchange_rate(target_currency: str) -> Decimal:
    # Intenta obtener tasa desde API; aplica fallback si falla
    try:
        resp = requests.get(EXCHANGE_API_URL, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            rate = data.get('rates', {}).get(target_currency)
            if rate is not None:
                return Decimal(str(rate))
    except Exception:
        pass
    # Fallback si falla la API
    return settings.EXCHANGE_RATE_FALLBACK

class BookViewSet(viewsets.ModelViewSet):
    # CRUD de libros + endpoints adicionales (search, low-stock, calculate-price)
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        # Filtro opcional por categoría via query param ?category=
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__iexact=category)
        return qs

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        # Búsqueda por categoría (paginada)
        category = request.query_params.get('category')
        if not category:
            return Response({'detail': 'Parámetro category es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        qs = self.get_queryset().filter(category__iexact=category)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        # Libros con stock por debajo del umbral ?threshold=
        try:
            threshold = int(request.query_params.get('threshold', '10'))
        except ValueError:
            return Response({'detail': 'threshold debe ser un entero.'}, status=status.HTTP_400_BAD_REQUEST)
        qs = self.get_queryset().filter(stock_quantity__lt=threshold)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='calculate-price')
    def calculate_price(self, request, pk=None):
        # Calcula precio local aplicando tasa y margen; persiste selling_price_local
        book = self.get_object()
        if book.cost_usd is None or book.cost_usd <= 0:
            return Response({'detail': 'cost_usd debe ser mayor a 0 para calcular precio.'}, status=status.HTTP_400_BAD_REQUEST)

        currency = settings.CURRENCY_DEFAULT
        rate = get_exchange_rate(currency)
        if rate is None:
            return Response({'detail': 'Servicio de tipo de cambio no disponible.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        cost_local = _quantize(Decimal(book.cost_usd) * rate)
        selling = _quantize(cost_local * (Decimal('1') + (settings.MARGIN_PERCENTAGE / Decimal('100'))))

        # Persistir el precio calculado
        book.selling_price_local = selling
        book.save(update_fields=['selling_price_local', 'updated_at'])

        payload = {
            'book_id': book.id,
            'cost_usd': Decimal(book.cost_usd),
            'exchange_rate': rate,
            'cost_local': cost_local,
            'margin_percentage': int(settings.MARGIN_PERCENTAGE),
            'selling_price_local': selling,
            'currency': currency,
            'calculation_timestamp': timezone.now().isoformat(),
        }
        return Response(payload, status=status.HTTP_200_OK)
