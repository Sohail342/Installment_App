from django.contrib import admin
from .models import Cart, CartItem 
# Register your models here.

@admin.register(Cart)
class CartAdminModel(admin.ModelAdmin):
    list_display = ('id','user', 'created_at', 'updated_at')
    search_fields = ('user', 'created_at', 'updated_at')
    list_filter = ['user']
    

@admin.register(CartItem)
class CartItemAdminModel(admin.ModelAdmin):
    list_display = ('id','cart', 'product', 'quantity', 'added_at')