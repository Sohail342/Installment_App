from django.contrib import admin
from . models import Product, Category

@admin.register(Category)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category_moto', 'date']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'price', 'inventory' ,'category']