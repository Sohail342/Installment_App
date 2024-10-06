from django.db import models
from account.models import User
from products.models import Product
from cart.models import Cart

class InstallmentPlan(models.Model):
    name = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField()  # Plan duration in months
    down_payment_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.duration_months} months"

class InstallmentPayment(models.Model):
    order_item = models.ForeignKey('OrderItem', related_name='installments', on_delete=models.CASCADE)
    month_number = models.PositiveIntegerField()  
    amount_due = models.DecimalField(max_digits=10, decimal_places=2) 
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    is_paid = models.BooleanField(default=False)  

    def __str__(self):
        return f"Installment {self.month_number} for {self.order_item.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    shipping_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=30, choices=[
        ('COD', 'Cash on Delivery'),
    ])
    installment_plan = models.CharField(max_length=30, choices=[
        ('3_months', '3 Months Plan'),
        ('6_months', '6 Months Plan'),
        ('9_months', '9 Months Plan'),
        ('12_months', '12 Months Plan'),
    ], default=None)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ], default='Pending')

    def __str__(self):
        return f"Order {self.id} for {self.user.name if self.user else 'Guest'}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Pre-calculated

    def __str__(self):
        return f"{self.quantity} x {self.product} in Order {self.order.id}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

