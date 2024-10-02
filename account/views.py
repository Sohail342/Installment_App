from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse
from .forms import UserRegForm, EmailLoginForm
from django.contrib.auth import authenticate

def signup(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = UserRegForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)  # Don't save yet, we may need to add more data
                user.set_password(form.cleaned_data['password1'])  # Set the password
                user.save()  
                login(request, user)
                return redirect(reverse("category_list"))
        else:
            form = UserRegForm()
        return render(request, 'account/signup.html', {'form': form})
    else:
        return redirect(reverse('category_list'))


def signin(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = EmailLoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = authenticate(username=email, password=password)

                if user is not None:
                    login(request, user)
                    
        else:
            form = EmailLoginForm()
        return render(request, 'account/signin.html', {'form': form})
    else:
        return redirect(reverse('category_list'))


def signout(request):
    logout(request)
    return redirect('account:signin')

