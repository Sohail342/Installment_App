from django.contrib import admin
from .models import Cart, CartItem 
from unfold.admin import ModelAdmin


@admin.register(Cart)
class CartAdminModel(ModelAdmin):
    list_display = ('id','user', 'created_at', 'updated_at')
    search_fields = ('user', 'created_at', 'updated_at')
    list_filter = ['user']
    

@admin.register(CartItem)
class CartItemAdminModel(ModelAdmin):
    list_display = ('id','cart', 'product', 'quantity', 'added_at')