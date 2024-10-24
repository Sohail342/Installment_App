# Generated by Django 5.1.1 on 2024-10-17 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0019_alter_order_total_bill'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='total_downpayment_price',
            new_name='downpayment_plus_form_fee',
        ),
        migrations.AddField(
            model_name='order',
            name='downpayment',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=10),
        ),
        migrations.AddField(
            model_name='order',
            name='monthly_installment',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Every Month', 'Every Month')], max_length=30),
        ),
    ]
