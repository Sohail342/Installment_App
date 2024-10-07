from django import forms

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
        ('Installment', 'Installment Payment'),
    ])

    
