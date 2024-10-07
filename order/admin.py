from django.contrib import admin
from .models import Order, OrderItem, InstallmentPayment

# Register your models here.

@admin.register(Order)
class OrderADminModel(admin.ModelAdmin):
    list_display = ('id','user', 'customer', 'cart','shipping_address', 'payment_method', 'is_paid', 'installment_plan')
    

@admin.register(OrderItem)
class OrderADminModel(admin.ModelAdmin):
    list_display = ('id','order', 'customer', 'product','quantity', 'price', 'total_price')
    
@admin.register(InstallmentPayment)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer','order_item', 'month_number', 'amount_due', 'amount_paid', 'is_paid')  