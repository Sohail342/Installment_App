from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart
from . models import Order, OrderItem, InstallmentPayment, DownPayment
from .forms import CheckoutForm
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from account.models import User, Customer
from django.utils import timezone
from django.db.models import Q


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from cart.models import Cart, CartItem
from .models import Order, OrderItem, InstallmentPayment
from .forms import CheckoutForm
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from account.models import User, Customer
from django.utils import timezone
from datetime import timedelta

@login_required(login_url='account:signin')
def checkout(request, user_id):
    user = get_object_or_404(User, id=user_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()
    
    cart_is_empty = cart_items.count() == 0
    subtotal = 0
    product_summaries = []

    for item in cart_items:
        product = item.product
        quantity = item.quantity
        installment_plan = item.installment_plan

        installment_details = product.get_installment_plan()

        down_payment = installment_details['down_payments'][installment_plan]
        monthly_payment = installment_details['installments'][installment_plan]
        total_amount = installment_details['total_amounts'][installment_plan]

        product_summaries.append({
            'product_name': product.name,
            'quantity': quantity,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'total_amount': total_amount,
            'installment_plan': installment_plan,
        })

        subtotal += down_payment

    total = subtotal + product.delivery_fee

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Extract form data
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            shipping_address = f"{form.cleaned_data['streetaddress']} {form.cleaned_data['apartment']}, {form.cleaned_data['towncity']}"
            payment_method = form.cleaned_data['payment_method']
            phone_number = form.cleaned_data['phone']
            email = form.cleaned_data['emailaddress']
            cnic = form.cleaned_data['cnic_no']

            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                cnic = cnic,
                defaults={
                    'first_name': firstname,
                    'last_name': lastname,
                    'email': email,
                    'address': shipping_address,
                    'phone_number':phone_number
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
                installment_plan=cart_items.first().installment_plan,  # Use first item for plan
                created_at=timezone.now(),
                updated_at=timezone.now(),
                is_paid=True,  # Set as paid since down payment is paid at checkout
            )

            # Create Down Payment
            DownPayment.objects.create(
            order=order,
            customer=customer,
            installment_form_fee = 500.00,    # physical form fee
            amount=subtotal,  # Use the subtotal as the down payment amount
        )

            # Create OrderItems and Installment Payments
            for item in cart_items:
                order_item = OrderItem.objects.create(
                    order=order,
                    customer=customer,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

                # Update product inventory
                product = item.product
                if product.inventory >= item.quantity:
                    product.inventory -= item.quantity
                    product.save()

                # Create Installment Payments
                months = int(item.installment_plan.split('_')[0])  # Get month count from plan
                for month in range(1, months + 1):
                    installment_payment = InstallmentPayment.objects.create(
                        order_item=order_item,
                        customer=customer,
                        month_number=month,
                        amount_due=monthly_payment,
                        amount_paid=0.00,
                        is_paid=False
                    )
                    # Set the due date (approximately 30 days per month)
                    installment_payment.due_date = timezone.now() + timedelta(days=month * 30)
                    installment_payment.save()

            # Clear the cart
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
    
    # Total orders by Sales Person
    total_orders = Order.objects.filter(user=request.user).count()
    
    # Prepare to calculate subtotal and delivery fee
    subtotal = 0
    delivery_fee = 0
    product_summaries = []

    # Loop through each item in the order
    for item in order.items.all():
        product = item.product
        quantity = item.quantity
        installment_plan = order.installment_plan

        installment_details = product.get_installment_plan()
        
        down_payment = installment_details['down_payments'][installment_plan]
        monthly_payment = installment_details['installments'][installment_plan]
        total_amount = installment_details['total_amounts'][installment_plan]

        product_summaries.append({
            'product_name': product.name,
            'quantity': quantity,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'total_amount': total_amount,
            'installment_plan': installment_plan,
        })

        subtotal += down_payment
        delivery_fee += product.delivery_fee  # Aggregate delivery fee

    total_price = subtotal + delivery_fee  

    return render(request, 'order/order_summary.html', {
        'order': order,
        'total_quantity': sum(item.quantity for item in order.items.all()),
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_price': total_price, 
        'product_summaries': product_summaries,
        'total_orders': total_orders,
    })





def total_bill_view(request):
    '''
    Total installment plan for all Customers
    '''

    # Get all instances of InstallmentPayment
    installments = InstallmentPayment.objects.all()

    # Get the search query
    search_query = request.GET.get('search', '')

    if search_query:
        # Filter by CNIC or phone number
        filters = Q(customer__cnic__icontains=search_query) | Q(customer__phone_number__icontains=search_query)
        installments = installments.filter(filters)

    # Group installments by customer
    grouped_installments = defaultdict(list)
    for installment in installments:
        grouped_installments[installment.customer].append(installment)

    # Pass the grouped installments to the template
    return render(request, 'order/installmentpayment_list.html', {
        "grouped_installments": dict(grouped_installments)
    })


    

