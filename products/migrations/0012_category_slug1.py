# Generated by Django 5.1.1 on 2024-11-11 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_rename_name_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug1',
            field=models.SlugField(default=None, max_length=300, null=True),
        ),
    ]
