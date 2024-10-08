from django import forms

class CheckoutForm(forms.Form):
    firstname = forms.CharField(max_length=100)
    lastname = forms.CharField(max_length=100, required=False)
    streetaddress = forms.CharField(max_length=255)
    apartment = forms.CharField(max_length=255, required=False)
    towncity = forms.CharField(max_length=100)
    postcodezip = forms.CharField(max_length=20, required=False)
    phone = forms.CharField(max_length=20)
    emailaddress = forms.EmailField(required=False)
    payment_method = forms.ChoiceField(choices=[
        ('Installment', 'Installment Payment'),
    ])

    
