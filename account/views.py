from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse
from django.contrib import messages
from .forms import  EmailLoginForm
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404, render
from .models import Customer
from collections import defaultdict

def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    installments = customer.installments.all()

    # Group installments by order item and include order ID
    grouped_installments = defaultdict(lambda: {'order_id': None, 'installments': []})
    for installment in installments:
        order_item = installment.order_item
        order_id = order_item.order.id  # Get the order ID
        grouped_installments[order_item]['order_id'] = order_id
        grouped_installments[order_item]['installments'].append(installment)

    return render(request, 'account/customer_detail.html', {
        'customer': customer,
        'grouped_installments': dict(grouped_installments),
    })


# def signup(request):
#     if not request.user.is_authenticated:
#         if request.method == 'POST':
#             form = UserRegForm(request.POST)
#             if form.is_valid():
#                 user = form.save(commit=False)
#                 user.set_password(form.cleaned_data['password1'])
#                 user.is_approved = False  # Set to False initially
#                 user.save()
#                 messages.info(request, "Registration successful! Please wait for approval.")
#                 return redirect(reverse("account:signin"))
#         else:
#             form = UserRegForm()
#         return render(request, 'account/signup.html', {'form': form})
#     else:
#         return redirect(reverse('products:category_list'))



def login_view(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = EmailLoginForm(request.POST) 
            if form.is_valid():
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password')
                user = authenticate(request=request, username=email, password=password)

                if user is not None:
                    if not user.is_approved:
                        messages.error(request, "Your account is not approved yet.")
                        return redirect(reverse('account:signin'))

                    login(request, user)
                    return redirect('dashboard:dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
        else:
            form = EmailLoginForm() 
    else:
        return redirect(reverse('dashboard:dashboard'))

    return render(request, 'account/signin.html', {'form': form})






def signout(request):
    logout(request)
    return redirect('account:signin')

