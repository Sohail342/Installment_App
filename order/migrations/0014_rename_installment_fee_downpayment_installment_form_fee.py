# Generated by Django 5.1.1 on 2024-10-10 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0013_alter_downpayment_installment_fee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='downpayment',
            old_name='installment_fee',
            new_name='installment_form_fee',
        ),
    ]
