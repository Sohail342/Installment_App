# Generated by Django 5.1.1 on 2025-04-23 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0027_installmentpayment_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
