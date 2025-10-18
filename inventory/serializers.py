from decimal import Decimal
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    # Serializer principal con validaciones de negocio
    class Meta:
        model = Book
        fields = '__all__'

    def validate_cost_usd(self, value: Decimal):
        # Debe ser mayor a 0
        if value is None or value <= 0:
            raise serializers.ValidationError('cost_usd debe ser mayor a 0.')
        return value

    def validate_stock_quantity(self, value: int):
        # No permite negativos
        if value is None or value < 0:
            raise serializers.ValidationError('stock_quantity no puede ser negativo.')
        return value

    def validate(self, attrs):
        # Mensaje claro ante ISBN duplicado al crear
        if self.instance is None:
            isbn = attrs.get('isbn')
            if isbn and Book.objects.filter(isbn=isbn).exists():
                raise serializers.ValidationError({'isbn': 'Ya existe un libro con ese ISBN.'})
        return attrs
