# Generated by Django 5.1.1 on 2024-10-21 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_guarantor'),
        ('order', '0024_order_guarantor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='guarantor',
        ),
        migrations.AddField(
            model_name='order',
            name='guarantors',
            field=models.ManyToManyField(blank=True, to='account.guarantor'),
        ),
    ]
