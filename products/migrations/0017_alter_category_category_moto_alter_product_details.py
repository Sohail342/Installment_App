# Generated by Django 5.1.1 on 2025-04-22 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_remove_product_delivery_fee_alter_category_photo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_moto',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='details',
            field=models.TextField(blank=True, null=True),
        ),
    ]
