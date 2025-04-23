from django.shortcuts import render, redirect
from django.contrib import messages
from cart.models import Cart, CartItem
from account.models import Guarantor
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
            total_amount = request.session.get('total_amount')

            # Set type is equal to static in order model
            installment_type = 'dynamic'

        # Total installments
        total_installments += current_installment_plan
        extracted_installments = re.findall(r'\d+', total_installments)   # Extract numbers from total_installments using regex

    # Calculate total
    total = form_fee + down_payment

    # Get payment type from cart item
    payment_type = 'installment'
    product_price = 0
    
    if cart_items.exists():
        cart_item = cart_items.first()
        payment_type = cart_item.payment_type
        product_price = cart_item.product.price
    
    # For cash payment, set total to product price
    if payment_type == 'cash':
        total = product_price

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        # For cash payments, make guarantor fields optional
        if payment_type == 'cash':
            for field_name in ['guaranteed_cnic_no', 'guaranteed_name', 'guaranteed_phone_no']:
                form.fields[field_name].required = False
                
        if form.is_valid():
            # Extract form data
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            shipping_address = f"{form.cleaned_data['streetaddress']} {form.cleaned_data['apartment']}, {form.cleaned_data['towncity']}"
            payment_method = form.cleaned_data.get('payment_method', 'Every Month')
            phone_number = form.cleaned_data['phone']
            email = form.cleaned_data['emailaddress']
            cnic = form.cleaned_data['cnic_no']


            # guarantor1 - only create for installment payments and if CNIC is provided (now optional)
            guarantor1 = None
            if payment_type != 'cash' and form.cleaned_data.get('guaranteed_cnic_no'):
                # Only create guarantor if both CNIC and name are provided
                if form.cleaned_data.get('guaranteed_name'):
                    guarantor1, created1 = Guarantor.objects.get_or_create(
                    cnic_no=form.cleaned_data['guaranteed_cnic_no'],
                    defaults={
                        'name': form.cleaned_data['guaranteed_name'],
                        'father_name': form.cleaned_data['guaranteed_father_name'],
                        'residential_address': form.cleaned_data['guaranteed_residential_address'],
                        'occupation': form.cleaned_data['guaranteed_occupation'],
                        'designation': form.cleaned_data['guaranteed_designation'],
                        'monthly_income': form.cleaned_data['guaranteed_monthly_income'],
                        'office_address': form.cleaned_data['guaranteed_office_address'],
                        'office_phone': form.cleaned_data['guaranteed_office_phone'],
                        'phone_no': form.cleaned_data['guaranteed_phone_no'],
                    }
                )

            # Create a second guarantor only if the fields are filled
            guarantor2 = None
            if form.cleaned_data['guaranteed2_cnic_no']:
                guarantor2, created2 = Guarantor.objects.get_or_create(
                    cnic_no=form.cleaned_data['guaranteed2_cnic_no'],
                    defaults={
                        'name': form.cleaned_data['guaranteed2_name'],
                        'father_name': form.cleaned_data['guaranteed2_father_name'],
                        'residential_address': form.cleaned_data['guaranteed2_residential_address'],
                        'occupation': form.cleaned_data['guaranteed2_occupation'],
                        'designation': form.cleaned_data['guaranteed2_designation'],
                        'monthly_income': form.cleaned_data['guaranteed2_monthly_income'],
                        'office_address': form.cleaned_data['guaranteed2_office_address'],
                        'office_phone': form.cleaned_data['guaranteed2_office_phone'],
                        'phone_no': form.cleaned_data['guaranteed2_phone_no'],
                    }
                )


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

            # Get payment type from cart item
            cart_item = cart.items.first()
            payment_type = cart_item.payment_type if cart_item else 'installment'
            
            # Create Order
            order = Order.objects.create(
                user=user,
                customer=customer,
                cart=cart,
                total_bill=total_amount if payment_type == 'installment' else product.price,  # For cash payment, use product price without fees
                downpayment_plus_form_fee = total if payment_type == 'installment' else product.price,  # For cash, full amount
                downpayment = down_payment if payment_type == 'installment' else product.price,  # For cash, full amount
                monthly_installment = monthly_installment if payment_type == 'installment' else 0,  # No installments for cash
                installment_type=installment_type if payment_type == 'installment' else 'none',
                shipping_address=shipping_address,
                payment_method='Cash' if payment_type == 'cash' else payment_method,
                installment_plan=current_installment_plan.replace('_', ' ') if payment_type == 'installment' else 'Full Payment',
                created_at=timezone.now(),
                updated_at=timezone.now(),
                is_paid=True,  # Set as paid for both cash and down payment
            )

            # Add guarantors to the order (only for installment payments)
            if payment_type != 'cash':
                if guarantor1:
                    order.guarantors.add(guarantor1)
                if guarantor2:
                    order.guarantors.add(guarantor2)

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
                
                # For cash payment, use product price as the total price
                # For installment, use the calculated total amount
                if item.payment_type == 'cash':
                    item_total_price = product.price
                else:
                    item_total_price = total_amount
                
                order_item = OrderItem.objects.create(
                    order=order,
                    customer=customer,
                    product=product,
                    quantity=item.quantity,
                    original_price=product.price,
                    installment_total_price=item_total_price,
                )

                # Update product inventory
                if product.inventory >= item.quantity:
                    product.inventory -= item.quantity
                    product.save()

                # Only create installment payments for installment type orders
                if item.payment_type == 'installment':
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
            return redirect('customer_reports:order_summary', order_id=order.id)

    else:
        form = CheckoutForm()
    
    
    return render(request, 'order/application_form.html', {
        'form': form,
        'cart_is_empty': cart_is_empty,
        'cart_items': cart_items,
        'down_payment_againts_hire': down_payment,
        'total': total,
        'monthly_installment': monthly_installment,
        'total_installments':''.join(extracted_installments),
        'payment_type': payment_type, 
        'product_price': product_price  
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
        # Filter by CNIC, phone number, or order ID
        filters = (
            Q(customer__cnic__icontains=clean_search_query) |
            Q(customer__phone_number__icontains=clean_search_query) |
            Q(order_item__order__id__icontains=clean_search_query) 
        )
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






    

