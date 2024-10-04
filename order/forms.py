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
        ('JazzCash', 'JazzCash'),
    ])
    installment_plan = forms.ModelChoiceField(queryset=InstallmentPlan.objects.all(), required=False)

    def clean_installment_plan(self):
        payment_method = self.cleaned_data.get('payment_method')
        installment_plan = self.cleaned_data.get('installment_plan')

        if payment_method == 'COD' and installment_plan is not None:
            raise forms.ValidationError("Installments are not available for Cash on Delivery.")
        return installment_plan
    
