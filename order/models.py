from django.db import models
from account.models import User, Customer
from products.models import Product
from cart.models import Cart


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders') 
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    shipping_address = models.TextField(null=True, blank=True)
    payment_method = models.CharField(max_length=30, choices=[
        ('Installment', 'Installment Payment'),
    ])
    installment_plan = models.CharField(max_length=30, choices=[
        ('3_months', '3 Months Plan'),
        ('6_months', '6 Months Plan'),
        ('9_months', '9 Months Plan'),
        ('12_months', '12 Months Plan'),
    ], default=None)
    
    # Track which installments are paid
    installment_status = models.TextField(default="", blank=True) 
    
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Paid', 'Paid'),
    ], default='Pending')

    def __str__(self):
        return f"Order {self.id} for {self.customer.first_name if self.customer else 'Guest'}"

    # Method to update installment status
    def update_installment_status(self):
        installments = self.items.first().installments.all()
        status = []
        for installment in installments:
            status.append(f"Month {installment.month_number}: {'Paid' if installment.is_paid else 'Unpaid'}")
        self.installment_status = ', '.join(status)
        self.save()
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='order_items') 
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Pre-calculated

    def __str__(self):
        return f"{self.quantity} x {self.product} in Order {self.order.id}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)
        

class InstallmentPayment(models.Model):
    order_item = models.ForeignKey('OrderItem', related_name='installments', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='installments')
    month_number = models.PositiveIntegerField()
    amount_due = models.IntegerField()
    amount_paid = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    initial_amount_due = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Track the original amount_due
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Installment {self.month_number} for {self.order_item.product.name}"

    def save(self, *args, **kwargs):
        if not self.pk:  # If it's a new record, store the initial amount_due
            self.initial_amount_due = self.amount_due

        if self.is_paid:
            # If marked as paid, set amount_paid equal to amount_due, and set amount_due to 0
            self.amount_paid = self.amount_due
            self.amount_due = 0
        else:
            # If not marked as paid, restore initial amount_due and reset amount_paid
            self.amount_due = self.initial_amount_due
            self.amount_paid = 0.00

        super().save(*args, **kwargs)

        # Check if all installments for the order item are paid
        all_installments_paid = all(installment.is_paid for installment in self.order_item.installments.all())

        # If all installments are paid, mark the order as paid
        if all_installments_paid:
            order = self.order_item.order
            order.is_paid = True
        else:
            # If not all installments are paid, ensure the order is not marked as paid
            order = self.order_item.order
            order.is_paid = False

        # Update installment status in the order
        order.update_installment_status()

        order.save()

class DownPayment(models.Model):
    order = models.ForeignKey(Order, related_name='down_payments', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='down_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    installment_form_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Down Payment of {self.amount} for Order {self.order.id}"


