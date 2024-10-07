from django.contrib import admin
from .models import Order, OrderItem, InstallmentPayment

class PaidFilter(admin.SimpleListFilter):
    title = 'Payment Status'
    parameter_name = 'is_paid'

    def lookups(self, request, model_admin):
        return (
            ('True', 'Paid'),
            ('False', 'Unpaid'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(is_paid=True)
        if self.value() == 'False':
            return queryset.filter(is_paid=False)
        return queryset

@admin.register(Order)
class OrderADminModel(admin.ModelAdmin):
    list_display = ('id','user', 'customer', 'cart', 'payment_method', 'is_paid', 'installment_plan')
    list_filter = ['user', PaidFilter, 'customer']

@admin.register(OrderItem)
class OrderADminModel(admin.ModelAdmin):
    list_display = ('id','order', 'customer', 'product','quantity', 'price', 'total_price')
    


@admin.register(InstallmentPayment)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_item', 'month_number', 'amount_due', 'amount_paid', 'is_paid')
    list_filter = (PaidFilter,) 