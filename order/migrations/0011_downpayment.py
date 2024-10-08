# Generated by Django 5.1.1 on 2024-10-10 15:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_user_is_approved'),
        ('order', '0010_installmentpayment_due_date_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='down_payments', to='account.customer')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='down_payments', to='order.order')),
            ],
        ),
    ]
