from django.core.validators import MinValueValidator
from django.db import models
from cloudinary.models import CloudinaryField

class Category(models.Model):
    name = models.CharField(max_length=50)
    category_moto = models.CharField(max_length=20)
    photo = CloudinaryField('products_category')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Categorie'
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    photo = CloudinaryField('products_images')
    price = models.IntegerField()
    details = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    inventory = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    delivery_fee = models.IntegerField(default=290)
    
    # Dynamic down payment percentages
    down_payment_3_months = models.FloatField(default=30.0) 
    down_payment_6_months = models.FloatField(default=20.0)  
    down_payment_9_months = models.FloatField(default=15.0)  
    down_payment_12_months = models.FloatField(default=10.0)  

    # Dynamic fee percentages
    fee_3_months = models.FloatField(default=10.0)  
    fee_6_months = models.FloatField(default=15.0)  
    fee_9_months = models.FloatField(default=20.0)  
    fee_12_months = models.FloatField(default=30.0)

    def __str__(self):
        return self.name

    def get_installment_plan(self):
        """
        Calculate installment plans for 3, 6, 9, and 12 months,
        including dynamic down payments, fees, and total amounts.
        """
        price = self.price
        
        # Dynamic down payment percentages
        down_payments = {  
            '3_months': int(price * (self.down_payment_3_months / 100)),
            '6_months': int(price * (self.down_payment_6_months / 100)),
            '9_months': int(price * (self.down_payment_9_months / 100)),
            '12_months': int(price * (self.down_payment_12_months / 100)),
        }

        # Calculate monthly installments and total amounts
        installments = {}
        total_amounts = {}
        
        for months in [3, 6, 9, 12]:
            key = f"{months}_months"
            
            # Calculate the base monthly payment (before adding fees)
            base_monthly_payment = (price - down_payments[key]) / months
            
            # Dynamically apply fee percentage based on the plan duration
            if months == 3:
                monthly_fee = base_monthly_payment * (self.fee_3_months / 100)
            elif months == 6:
                monthly_fee = base_monthly_payment * (self.fee_6_months / 100)
            elif months == 9:
                monthly_fee = base_monthly_payment * (self.fee_9_months / 100)
            elif months == 12:
                monthly_fee = base_monthly_payment * (self.fee_12_months / 100)
            
            # Final monthly payment after adding the fee
            final_monthly_payment = int(base_monthly_payment + monthly_fee)
            
            # Store the final monthly payment in the installments dictionary
            installments[key] = final_monthly_payment
            
            # Calculate the total amount: down payment + (final monthly payment * months)
            total_amounts[key] = down_payments[key] + (final_monthly_payment * months)

        return {
            'installments': installments,
            'down_payments': down_payments,
            'total_amounts': total_amounts,
        }
    
    
    def calculate_dynamic_installment_plan(self, user_down_payment, user_months):
        """
        Calculate installment plan based on user input for down payment and months.
        """
        price = self.price
        user_down_payment = int(user_down_payment)
        user_months = int(user_months)


        # installment feed
        installment_fee = int(price * ( 40 / 100))

        # update Total price 
        new_price = price+installment_fee

        # Validate user down payment
        if user_down_payment < 0 or user_down_payment > new_price:
            raise ValueError("Invalid down payment amount.")

        # Calculate the base monthly payment
        monthly_payment = (new_price - user_down_payment) / user_months
        
        # Round Off float monthly payment
        monthly_payment = round(monthly_payment)

        # Calculate the total amount
        total_amount = int(user_down_payment + (monthly_payment * user_months))

        return {
            'monthly_payment': monthly_payment,
            'total_amount': total_amount,
            'down_payment':user_down_payment,
            'installment_plan':user_months
        }
