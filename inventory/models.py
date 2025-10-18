import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

def validate_isbn(value: str):
    # Acepta ISBN con guiones, exige 10 o 13 dígitos efectivos
    digits = re.sub(r'[^0-9]', '', value or '')
    if len(digits) not in (10, 13):
        raise ValidationError('ISBN debe contener 10 o 13 dígitos (se permiten guiones).')

class Book(models.Model):
    # Modelo de libro con restricciones de negocio (ISBN único, stock >= 0, cost_usd > 0)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=17, unique=True, validators=[validate_isbn])
    cost_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    selling_price_local = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100)
    supplier_country = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # últimos creados primero

    def __str__(self):
        return f'{self.title} - {self.isbn}'
