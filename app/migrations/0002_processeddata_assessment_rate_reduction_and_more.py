# Generated by Django 4.2.7 on 2025-06-10 08:56

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='processeddata',
            name='assessment_rate_reduction',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5),
        ),
        migrations.AddField(
            model_name='processeddata',
            name='property_tax_for_loan_period',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20),
        ),
    ]
