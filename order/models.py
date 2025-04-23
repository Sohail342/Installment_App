from django.db import models
from account.models import User, Customer, Guarantor
from products.models import Product
from cart.models import Cart
from django.utils import timezone


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders') 
    guarantors = models.ManyToManyField(Guarantor, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    downpayment_plus_form_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_bill = models.DecimalField(max_digits=10, decimal_places=2)
    downpayment = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    shipping_address = models.TextField(null=True, blank=True)
    installment_type = models.CharField(max_length=100, default=None)
    payment_method = models.CharField(max_length=30, choices=[
        ('Every Month', 'Every Month'),
        ('Cash', 'Cash'),
    ])
    installment_plan = models.CharField(max_length=30)
    
    # Track which installments are paid
    installment_status = models.TextField(default="", blank=True) 
    
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Paid', 'Paid'),
    ], default='Pending')
    
    # Total balance field to store the sum of all installment balances
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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
        
    def update_total_balance(self):
        """Calculate and update the total balance for this order by summing all installment balances."""
        total = 0
        for item in self.items.all():
            for installment in item.installments.all():
                total += installment.balance
        self.total_balance = total
        self.save(update_fields=['total_balance'])
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='order_items') 
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)  
    installment_total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product} in Order {self.order.id}"
        

class InstallmentPayment(models.Model):
    order_item = models.ForeignKey('OrderItem', related_name='installments', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='installments')
    month_number = models.PositiveIntegerField()
    amount_due = models.IntegerField()
    amount_paid = models.IntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    initial_amount_due = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Track the original amount_due
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Installment {self.month_number} for {self.order_item.product.name}"
    

    @property
    def remaining_amount(self):
        """Calculate the remaining amount for this installment."""
        return max(0, self.amount_due - self.amount_paid)
    
    @property
    def paid_amount(self):
        """Calculate the paid amount."""
        return self.amount_paid
    
    @property
    def due_amount(self):
        """Calculate the due amount."""
        return self.amount_due
    
    @staticmethod
    def upcoming_due_dates(order_item=None):
        """Return a list of upcoming due dates for unpaid installments."""
        now = timezone.now()
        queryset = InstallmentPayment.objects.filter(due_date__gt=now, is_paid=False)
        if order_item:
            queryset = queryset.filter(order_item=order_item)
        return list(queryset.values_list('due_date', flat=True))
    

    def save(self, *args, **kwargs):
        from decimal import Decimal
        
        # Convert amount_paid to Decimal to match initial_amount_due type
        if isinstance(self.amount_paid, float):
            self.amount_paid = Decimal(str(self.amount_paid))
        
        # Get previous state if this is an existing record
        if self.pk:
            try:
                original = InstallmentPayment.objects.get(pk=self.pk)
                previous_paid = original.amount_paid
                # If this is the first save, ensure we have the initial amount due
                if not self.initial_amount_due:
                    self.initial_amount_due = original.initial_amount_due
            except InstallmentPayment.DoesNotExist:
                previous_paid = 0
        else:
            # If it's a new record, store the initial amount_due
            self.initial_amount_due = self.amount_due
            previous_paid = 0
        
        # Calculate how much is being paid in this transaction
        current_payment = self.amount_paid - previous_paid
        
        # Handle payment status
        if self.is_paid:
            # If manually marked as paid, ensure amount_paid at least equals initial_amount_due
            if self.amount_paid < self.initial_amount_due:
                self.amount_paid = self.initial_amount_due
            self.amount_due = 0
        else:
            # For partial payments, update amount_due to reflect the remaining balance
            self.amount_due = max(0, self.initial_amount_due - self.amount_paid)
            
            # If amount_paid equals or exceeds initial_amount_due, mark as paid
            if self.amount_paid >= self.initial_amount_due:
                self.is_paid = True
                self.amount_due = 0
        
        # Calculate the remaining amount that should be paid
        remaining_due = self.initial_amount_due - self.amount_paid
        
        # Update the balance field based on the remaining due
        if remaining_due > 0:  # Underpayment
            # Balance is the remaining amount to be paid
            self.balance = remaining_due
        elif remaining_due < 0:  # Overpayment
            # There's an overpayment, set balance to 0 for this installment
            self.balance = 0
            # Store the overpayment amount to distribute to other installments
            overpayment = abs(remaining_due)
        else:  # Exact payment
            # No balance needed
            self.balance = 0
            overpayment = 0

        # Save this installment first
        super().save(*args, **kwargs)

        # If there's an overpayment, distribute it to other unpaid installments
        if remaining_due < 0:
            self.distribute_overpayment(abs(remaining_due))

        # Check if all installments for the order item are paid
        all_installments_paid = all(installment.is_paid for installment in self.order_item.installments.all())

        # Update order payment status
        order = self.order_item.order
        order.is_paid = all_installments_paid
        order.update_installment_status()
        
        # Update the order's total balance
        order.update_total_balance()
        
    def distribute_overpayment(self, overpayment_amount):
        """Distribute overpayment to future unpaid installments."""
        if overpayment_amount <= 0:
            return
            
        # Get all unpaid installments for this order item, ordered by month_number
        future_installments = InstallmentPayment.objects.filter(
            order_item=self.order_item,
            is_paid=False
        ).exclude(pk=self.pk).order_by('month_number')
        
        # If no future installments, nothing to do
        if not future_installments.exists():
            return
            
        # Distribute the overpayment to each future installment
        for installment in future_installments:
            if overpayment_amount <= 0:
                break
                
            # Calculate how much can be applied to this installment
            applicable_amount = min(overpayment_amount, installment.amount_due)
            
            if applicable_amount > 0:
                # Update the installment with the applied amount
                installment.amount_paid += applicable_amount
                overpayment_amount -= applicable_amount
                
                # Check if this payment fully covers the installment
                if installment.amount_paid >= installment.initial_amount_due:
                    installment.is_paid = True
                    installment.amount_due = 0
                else:
                    # Update the remaining due amount
                    installment.amount_due = installment.initial_amount_due - installment.amount_paid
                
                # Update the balance field
                installment.balance = max(0, installment.amount_due)
                
                # Save the installment without triggering the save method recursively
                super(InstallmentPayment, installment).save()


class DownPayment(models.Model):
    order = models.ForeignKey(Order, related_name='down_payments', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='down_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    installment_form_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Down Payment of {self.amount} for Order {self.order.id}"


