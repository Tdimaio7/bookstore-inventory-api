from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal
import inventory.models

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('isbn', models.CharField(max_length=17, unique=True, validators=[inventory.models.validate_isbn])),
                ('cost_usd', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('selling_price_local', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('stock_quantity', models.PositiveIntegerField(default=0)),
                ('category', models.CharField(max_length=100)),
                ('supplier_country', models.CharField(max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
