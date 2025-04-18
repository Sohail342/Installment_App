# Generated by Django 5.1.1 on 2024-10-21 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_remove_guarantor_guarantor2_home_phone_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_cnic_no',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_designation',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_father_name',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_monthly_income',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_name',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_occupation',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_office_address',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_office_phone',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_phone_no',
        ),
        migrations.RemoveField(
            model_name='guarantor',
            name='guarantor2_residential_address',
        ),
        migrations.AlterField(
            model_name='guarantor',
            name='cnic_no',
            field=models.CharField(max_length=15),
        ),
    ]
