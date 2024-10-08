from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart, CartItem
from . models import Order, OrderItem, InstallmentPayment
from .forms import CheckoutForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from account.models import User, Customer
from django.utils import timezone


@login_required(login_url='account:signin')
def checkout(request, user_id):
    user = get_object_or_404(User, id=user_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()
    cart_product = CartItem.objects.get(cart=cart)

    cart_is_empty = cart_items.count() == 0
    cart_items = CartItem.objects.filter(cart=cart)

    product_summaries = []
    subtotal = 0

    for item in cart_items:
        product = item.product
        quantity = item.quantity
        installment_plan = item.installment_plan  

        installment_details = product.get_installment_plan()

        if installment_plan == '3_months':
            down_payment = installment_details['down_payments']['3_months']
            monthly_payment = installment_details['installments']['3_months']
            total_amount = installment_details['total_amounts']['3_months']
            
        elif installment_plan == '6_months':
            down_payment = installment_details['down_payments']['6_months']
            monthly_payment = installment_details['installments']['6_months']
            total_amount = installment_details['total_amounts']['6_months']
            
        elif installment_plan == '9_months':
            down_payment = installment_details['down_payments']['9_months']
            monthly_payment = installment_details['installments']['9_months']
            total_amount = installment_details['total_amounts']['9_months']
            
        elif installment_plan == '12_months':
            down_payment = installment_details['down_payments']['12_months']
            monthly_payment = installment_details['installments']['12_months']
            total_amount = installment_details['total_amounts']['12_months']

        product_summaries.append({
            'product_name': product.name,
            'quantity': quantity,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'total_amount': total_amount,
            'installment_plan': installment_plan,
        })

        subtotal += down_payment

    total = product.delivery_fee + subtotal

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            shipping_address = f"{form.cleaned_data['streetaddress']} {form.cleaned_data['apartment']}, {form.cleaned_data['towncity']}, {form.cleaned_data['postcodezip']}"
            payment_method = form.cleaned_data['payment_method']
            phone_number = form.cleaned_data['phone']
            email = form.cleaned_data['emailaddress']
            
            # Check if the customer already exists based on phone number
            customer, created = Customer.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'first_name': firstname,
                    'last_name': lastname,
                    'email': email,
                    'address': shipping_address,
                }
            )
            

            # Create Order
            order = Order.objects.create(
                user=user,
                customer=customer,
                cart=cart,
                total_price=total,
                shipping_address=shipping_address,
                payment_method=payment_method,
                installment_plan=cart_product.installment_plan,
                created_at=timezone.now(),
                updated_at=timezone.now(),
                is_paid=True,  # Set as paid since down payment is paid at checkout
            )
            order.save()
            
            
            # Create OrderItems
            for item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    customer=customer,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

                 # Decrease the product quantity
                product = item.product
                if product.inventory >= item.quantity:
                    product.inventory -= item.quantity
                    product.save()

                # Create Installment Payments
                product = item.product
                installment_plan = item.installment_plan
                installment_details = product.get_installment_plan()

                months = 0
                if installment_plan == '3_months':
                    months = 3
                    monthly_payment = installment_details['installments']['3_months']
                elif installment_plan == '6_months':
                    months = 6
                    monthly_payment = installment_details['installments']['6_months']
                elif installment_plan == '9_months':
                    months = 9
                    monthly_payment = installment_details['installments']['9_months']
                elif installment_plan == '12_months':
                    months = 12
                    monthly_payment = installment_details['installments']['12_months']

                # Create Installment Payments for each month
                for month in range(1, months + 1):
                    InstallmentPayment.objects.create(
                        order_item=order_item,  
                        customer=customer,
                        month_number=month,
                        amount_due=monthly_payment,
                        amount_paid=0.00,
                        is_paid=False
                    )

            cart.items.all().delete()

            messages.success(request, 'Order placed and installment plan created successfully!')
            return redirect('order:order_summary', order_id=order.id)
    else:
        form = CheckoutForm()
    
    return render(request, 'order/checkout.html', {
        'form': form,
        'cart_is_empty': cart_is_empty,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'product_delivery_fee': product.delivery_fee,
    })


    

def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # List to store detailed product summary for each product
    product_summaries = []
    
    # Loop through each item in the order and get the necessary details
    for item in order.items.all():
        product = item.product
        quantity = item.quantity
        installment_plan = item.order.installment_plan

        # Get installment plan details for this product
        installment_details = product.get_installment_plan()

        # Depending on the selected installment plan, get specific details
        if installment_plan == '3_months':
            down_payment = installment_details['down_payments']['3_months']
            monthly_payment = installment_details['installments']['3_months']
            total_amount = installment_details['total_amounts']['3_months']
            
        elif installment_plan == '6_months':
            down_payment = installment_details['down_payments']['6_months']
            monthly_payment = installment_details['installments']['6_months']
            total_amount = installment_details['total_amounts']['6_months']
            
        elif installment_plan == '9_months':
            down_payment = installment_details['down_payments']['9_months']
            monthly_payment = installment_details['installments']['9_months']
            total_amount = installment_details['total_amounts']['9_months']
            
        elif installment_plan == '12_months':
            down_payment = installment_details['down_payments']['12_months']
            monthly_payment = installment_details['installments']['12_months']
            total_amount = installment_details['total_amounts']['12_months']

        # Append the product summary to the list
        product_summaries.append({
            'product_name': product.name,
            'quantity': quantity,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'total_amount': total_amount,
            'installment_plan': installment_plan,
        })
    
    # Calculate the total quantity and subtotal for the entire order
    total_quantity = sum(item.quantity for item in order.items.all())

    return render(request, 'order/order_summary.html', {
        'order': order,
        'total_quantity': total_quantity,
        'subtotal': down_payment,
        'product_summaries': product_summaries, 
        'delivery_fee': product.delivery_fee,
    })

