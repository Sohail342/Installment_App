from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.

@admin.register(Order)
class OrderADminModel(admin.ModelAdmin):
    list_display = ('id','user', 'cart','shipping_address', 'payment_method', 'is_paid', 'installment_plan')
    

@admin.register(OrderItem)
class OrderADminModel(admin.ModelAdmin):
    list_display = ('id','order', 'product','quantity', 'price', 'total_price')