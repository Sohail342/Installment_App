from django import forms
from django.contrib.auth import authenticate
from . models import User


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Extract request from kwargs
        super(EmailLoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            print("Email:", email, "and password:",password )
            user = authenticate(email=email, password=password)
            use = User.objects.all()
            print("user", user)
            print("All users\n", use)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
        return cleaned_data
