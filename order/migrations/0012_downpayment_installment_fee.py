# Generated by Django 5.1.1 on 2024-10-10 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0011_downpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='downpayment',
            name='installment_fee',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=10),
        ),
    ]
