from django.contrib import admin
from . models import Product, Category

@admin.register(Category)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category_moto', 'date']
    search_fields = ['name']
    list_filter = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'price', 'inventory' ,'category']
    search_fields = ['name']
    list_filter = ('name',)