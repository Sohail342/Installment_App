# Generated by Django 5.1.1 on 2024-10-21 16:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_guarantor'),
        ('order', '0023_remove_installmentpayment_balance_amout'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='guarantor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.guarantor'),
        ),
    ]
