from django.contrib import admin
from .models import Order, OrderItem, InstallmentPayment, DownPayment

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
    list_display = ('id','user', 'customer', 'customer_cnic', 'cart', 'payment_method', 'is_paid', 'installment_plan')
    list_filter = ['user', PaidFilter, 'customer']
    readonly_fields = ['created_at', 'updated_at', 'installment_plan']

    def customer_cnic(self, obj):
        return obj.customer.cnic
    customer_cnic.short_description = 'Customer CNIC No'




@admin.register(OrderItem)
class OrderItemADminModel(admin.ModelAdmin):
    list_display = ('id','order', 'customer', 'customer_cnic', 'product','quantity', 'price', 'total_price')

    def customer_cnic(self, obj):
        return obj.customer.cnic
    
    customer_cnic.short_description = 'Customer CNIC No'
    



@admin.register(InstallmentPayment)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'customer_cnic', 'order_item', 'month_number', 'amount_due', 'amount_paid', 'is_paid')
    list_filter = (PaidFilter,) 

    def customer_cnic(self, obj):
        return obj.customer.cnic
    customer_cnic.short_description = 'Customer CNIC No'




@admin.register(DownPayment)
class DowpaymentADminModel(admin.ModelAdmin):
    list_display = ('id','order', 'customer', 'customer_cnic', 'amount','payment_date')
    list_filter = ('payment_date',) 

    def customer_cnic(self, obj):
        return obj.customer.cnic
    customer_cnic.short_description = 'Customer CNIC No'