from django import forms
from .models import InstallmentPlan

class CheckoutForm(forms.Form):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100)
    streetaddress = forms.CharField(max_length=255)
    apartment = forms.CharField(max_length=255, required=False)
    towncity = forms.CharField(max_length=100)
    postcodezip = forms.CharField(max_length=20)
    phone = forms.CharField(max_length=20)
    emailaddress = forms.EmailField()
    payment_method = forms.ChoiceField(choices=[
        ('COD', 'Cash on Delivery'),
    ])
    installment_plan = forms.ChoiceField(choices=[
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('9_months', '9 Months'),
        ('12_months', '12 Months'),
    ])

    
