from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart, CartItem
from . models import Order, OrderItem
from .forms import CheckoutForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from account.models import User
from django.utils import timezone
from products.models import Product

@login_required(login_url='account:signin')
def checkout(request, user_id):
    user = get_object_or_404(User, id=user_id)
    product_delivery_fee = Product.objects.get(pk=user_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()

    # Check if the cart is empty
    cart_is_empty = cart_items.count() == 0

    subtotal = sum(item.total_price() for item in cart_items)
    total = product_delivery_fee.delivery_fee + subtotal  # Add delivery charges

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        print(form.errors)
        if form.is_valid():
            # Collect data from the form
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            shipping_address = f"{form.cleaned_data['streetaddress']} {form.cleaned_data['apartment']}, {form.cleaned_data['towncity']}, {form.cleaned_data['postcodezip']}"
            payment_method = form.cleaned_data['payment_method']
            # installment_plan = [item.installment_plan for item in cart_items if item.installment_plan]
            installment_plan = form.cleaned_data['payment_method']
            
            
            # Apply installment plan logic
            # if installment_plan:
            #     down_payment = (installment_plan.down_payment_percentage / 100) * subtotal
            #     fee = (installment_plan.fee_percentage / 100) * subtotal
            #     total += fee
            # else:
            #     down_payment = total  # Full payment for non-installment

            # Create order
            order = Order.objects.create(
                user=user,
                cart=cart,
                total_price=total,
                shipping_address=shipping_address,
                payment_method=payment_method,
                # installment_plan="installment_plan",
                created_at=timezone.now(),
                updated_at=timezone.now(),
                is_paid=False,
            )
            order.save()

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Reduce product inventory
            for item in cart_items:
                product = item.product
                product.inventory -= item.quantity
                product.save()

            cart.items.all().delete()  # Clear the cart

            messages.success(request, 'Order placed successfully!')
            # send_email(form.cleaned_data['emailaddress'], 'send_emails/successful_order.html')
            print("order placed")
            return redirect('order:order_summary', order_id=order.id)
    else:
        form = CheckoutForm()

    return render(request, 'order/checkout.html', {
        'form': form,
        'cart_is_empty': cart_is_empty,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'product_delivery_fee':product_delivery_fee.delivery_fee,
    })

    

def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Calculate total quantity and subtotal for the order
    total_quantity = sum(item.quantity for item in order.items.all())
    subtotal = sum(item.total_price for item in order.items.all())  # Directly access field
    
    return render(request, 'order/order_summary.html', {
        'order': order,
        'total_quantity': total_quantity,
        'subtotal': subtotal,
    })

