from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart, CartItem
from django.core.paginator import Paginator
from . models import Order, OrderItem, InstallmentPayment, DownPayment
from .forms import CheckoutForm
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from account.models import User, Customer
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
import re



@login_required(login_url='account:signin')
def checkout(request, user_id):
    user = get_object_or_404(User, id=user_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()

    cartItem, created = CartItem.objects.get_or_create(cart=cart)
    
    cart_is_empty = cart_items.count() == 0
    down_payment = 0
    monthly_installment = 0
    total_installments = ''
    installment_type = ''
    form_fee = 500  # physical form fee (fixed)
    product_summaries = []

    # Store the first installment plan to use in Order
    installment_plan = None

    for item in cart_items:
        product = item.product
        quantity = item.quantity
        current_installment_plan = item.installment_plan
        
        # If it's the first item, set the installment plan
        if installment_plan is None:
            installment_plan = current_installment_plan

        # For static Installment Plan
        if cartItem.installment_type == 'static':
            # Get installment details for the current product
            installment_details = product.get_installment_plan()

            down_payment = installment_details['down_payments'][current_installment_plan]
            monthly_installment = installment_details['installments'][current_installment_plan]
            total_amount = installment_details['total_amounts'][current_installment_plan]

            product_summaries.append({
                'product_name': product.name,
                'quantity': quantity,
                'down_payment': down_payment,
                'monthly_payment': monthly_installment,
                'total_amount': total_amount,
                'installment_plan': current_installment_plan,
            })

            # Set type is equal to static in order model
            installment_type = 'static'

        # For Dynamic Installment Plan
        elif cartItem.installment_type == 'dynamic':
            down_payment = request.session.get('down_payment')
            installment_plan = request.session.get('installment_plan')
            monthly_installment = request.session.get('monthly_payment')
            print(monthly_installment)
            total_amount = request.session.get('total_amount')

            # Set type is equal to static in order model
            installment_type = 'dynamic'

        # Total installments
        total_installments += current_installment_plan
        extracted_installments = re.findall(r'\d+', total_installments)   # Extract numbers from total_installments using regex

    # Calculate total
    total = form_fee + down_payment

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
            guaranteed_cnic_no = form.cleaned_data['guaranteed_cnic_no']

            # Get or create customer
            customer, created = Customer.objects.get_or_create(
                cnic=cnic.replace('-', ''),
                defaults={
                    'first_name': firstname,
                    'last_name': lastname,
                    'email': email,
                    'address': shipping_address,
                    'phone_number': phone_number
                }
            )

            # Create Order
            order = Order.objects.create(
                user=user,
                customer=customer,
                cart=cart,
                total_price=total,
                installment_type=installment_type,
                shipping_address=shipping_address,
                payment_method=payment_method,
                installment_plan=current_installment_plan,  # Use the determined installment plan
                created_at=timezone.now(),
                updated_at=timezone.now(),
                is_paid=True,  # Set as paid since down payment is paid at checkout
            )

            # Create Down Payment
            DownPayment.objects.create(
                order=order,
                customer=customer,
                installment_form_fee=form_fee,
                amount=down_payment,  # Use the down_payment_againts_hire as the down payment amount
            )

            # Create OrderItems and Installment Payments

            monthly_payment = 0

            for item in cart_items:
                product = item.product
                order_item = OrderItem.objects.create(
                    order=order,
                    customer=customer,
                    product=product,
                    quantity=item.quantity,
                    price=product.price
                )

                # Update product inventory
                if product.inventory >= item.quantity:
                    product.inventory -= item.quantity
                    product.save()

                # Get the installment plan for this item
                months = int(item.installment_plan.split('_')[0])  # Get month count from plan

                if cartItem.installment_type == 'static':
                    installment_details = product.get_installment_plan()
                    monthly_payment = installment_details['installments'][item.installment_plan]
                
                elif cartItem.installment_type == 'dynamic':
                    monthly_payment = request.session.get('monthly_payment')

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
    return render(request, 'order/application_form.html', {
        'form': form,
        'cart_is_empty': cart_is_empty,
        'cart_items': cart_items,
        'down_payment_againts_hire': down_payment,
        'total': total,
        'monthly_installment': monthly_installment,
        'total_installments':''.join(extracted_installments)
    })



@login_required(login_url='account:signin')
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Total orders by Sales Person
    total_orders = Order.objects.filter(user=request.user).count()
    
    # Prepare to calculate down_payment_againts_hire and delivery fee
    down_payment = 0
    product_summaries = []
    monthly_payment = 0

    # Loop through each item in the order
    for item in order.items.all():
        product = item.product
        quantity = item.quantity
        installment_plan = order.installment_plan

        if order.installment_type == "static":
            installment_details = product.get_installment_plan()
            
            down_payment = installment_details['down_payments'][installment_plan]
            monthly_payment = installment_details['installments'][installment_plan]
            total_amount = installment_details['total_amounts'][installment_plan]

        elif order.installment_type == "dynamic":
            down_payment = request.session.get('down_payment')
            installment_plan = request.session.get('installment_plan')
            monthly_payment = request.session.get('monthly_payment')
            total_amount = request.session.get('total_amount')
            print(down_payment)

        product_summaries.append({
            'product_name': product.name,
            'quantity': quantity,
            'down_payment': down_payment,
            'monthly_payment': monthly_payment,
            'total_amount': total_amount,
            'installment_plan': installment_plan,
        })



    return render(request, 'order/order_summary.html', {
        'order': order,
        'total_quantity': sum(item.quantity for item in order.items.all()),
        'down_payment': down_payment,
        'monthly_payment': monthly_payment,
        'product_summaries': product_summaries,
        'total_orders': total_orders,
    })




@login_required(login_url='account:signin')
def total_bill_view(request):
    '''
    Total installment plan for all Customers
    '''

    # Get all instances of InstallmentPayment
    installments = InstallmentPayment.objects.all().order_by('customer')

    # Get the search query
    search_query = request.GET.get('search', '')
    clean_search_query = search_query.strip()

    clean_search_query = clean_search_query.replace("-", '')

    if clean_search_query:
        # Filter by CNIC or phone number
        filters = Q(customer__cnic__icontains=clean_search_query) | Q(customer__phone_number__icontains=clean_search_query)
        installments = installments.filter(filters).order_by('customer')


    # Set up pagination
    paginator = Paginator(installments, 38)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Group installments by customer
    grouped_installments = defaultdict(list)
    for installment in page_obj:
        grouped_installments[installment.customer].append(installment)

    
    return render(request, 'order/installmentpayment_list.html', {
        "grouped_installments": dict(grouped_installments),
        "page_obj": page_obj,
    })



@login_required(login_url='account:signin')
def dynamic_installment_details(request):
    # Retrieve data from session
    down_payment = request.session.get('down_payment')
    installment_plan = request.session.get('installment_plan')
    monthly_payment = request.session.get('monthly_payment')
    total_amount = request.session.get('total_amount')
    product_inventory = request.session.get('product')
    product_id = request.session.get('product_id')

    
    return render(request, 'order/dynamic_installment_details.html', {
        'down_payment': down_payment,
        'installment_plan': installment_plan,
        'monthly_payment': monthly_payment,
        'total_amount': total_amount,
        'product_inventory':product_inventory,
        "product_id":product_id
    })






    

