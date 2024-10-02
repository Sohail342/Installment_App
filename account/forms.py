from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import authenticate


class UserRegForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'terms_conditions']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'terms_conditions': forms.CheckboxInput(attrs={'class': 'form-check-input', 'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        errors = []

        if len(name) < 5:
            errors.append('Name must be greater than 5 characters.')

        if any(char.isdigit() for char in name):
            errors.append('Name should not contain numeric values.')

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data



class EmailLoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
        return cleaned_data

