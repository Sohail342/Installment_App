# Generated by Django 5.1.1 on 2024-10-21 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_guarantor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guarantor',
            name='cnic_no',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='guarantor',
            name='guarantor2_cnic_no',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
