from django import forms
import re

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

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("phone")
        name = cleaned_data.get('firstname')
        
        errors = []

        if name:
            if len(name) < 5:
                errors.append('Name must contains atleast 5 characters')

        # Pakistani Mobile Number Pattern
        phone_pattern = re.compile(r'^((\+92 ?)|0)?(3[0-9]{2})[0-9]{7}$')

        if phone_number:
            if not phone_pattern.match(phone_number):
                errors.append('Enter a valid mobile number (e.g., 03001234567 or +92 3001234567).')

        if errors:
            raise forms.ValidationError(errors)
    

    
