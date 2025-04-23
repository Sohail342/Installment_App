import csv
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse, JsonResponse
from io import BytesIO
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from order.models import InstallmentPayment
from account.models import Customer, Guarantor
from order.models import Order, OrderItem, InstallmentPayment



def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Fetch installments for the order items
    installments = InstallmentPayment.objects.filter(order_item__in=order_items)

    # Extract numbers from total_installments using regex
    total_installments = order.installment_plan
    extracted_installments = "".join(re.findall(r'\d+', total_installments)) 

    # Return a list of due dates of upcoming unpaid installments for this order
    due_dates = []
    for item in order_items:
        due_dates.extend(InstallmentPayment.upcoming_due_dates(order_item=item))
    
    # Get the first upcoming due date if available
    due_date = due_dates[0] if due_dates else None

    # Find balance
    balance = sum(installment.balance for installment in installments)

    context = {
        'order': order,
        'order_items': order_items,
        'installments': installments,
        'balance': balance,
        'extracted_installments': extracted_installments,
        'due_date': due_date,  # First upcoming due date
    }
        
    return render(request, 'customer_reports/order_summary.html', context)





def customer_list(request):
    # Get search query if any
    search_query = request.GET.get('search', '')
    
    # Filter customers based on search query
    if search_query:
        customers = Customer.objects.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(cnic__icontains=search_query) | 
            Q(phone_number__icontains=search_query)
        ).order_by('first_name')
    else:
        customers = Customer.objects.all().order_by('first_name')
    
    # Calculate order summary data
    total_balance = 0
    total_due = 0
    total_paid = 0
    customer_data = {}
    
    for customer in customers:
        # Get all orders for this customer
        orders = Order.objects.filter(customer=customer)
        customer_balance = 0
        customer_due = 0
        customer_paid = 0
        
        for order in orders:
            # Get all installments for this order
            order_items = OrderItem.objects.filter(order=order)
            installments = InstallmentPayment.objects.filter(order_item__in=order_items)
            
            # Calculate balance, due and paid amounts
            for installment in installments:
                customer_balance += installment.balance
                customer_due += installment.due_amount
                customer_paid += installment.paid_amount
        
        # Store customer data
        customer_data[customer.id] = {
            'balance': customer_balance,
            'due': customer_due,
            'paid': customer_paid,
            'orders_count': orders.count()
        }
        
        # Add to totals
        total_balance += customer_balance
        total_due += customer_due
        total_paid += customer_paid
    
    # Pagination
    paginator = Paginator(customers, 10)  # Show 10 customers per page
    page_number = request.GET.get('page')
    customers_page = paginator.get_page(page_number)
    
    context = {
        'customers': customers_page,
        'customer_data': customer_data,
        'total_balance': total_balance,
        'total_due': total_due,
        'total_paid': total_paid
    }
    
    return render(request, 'customer_reports/customer_list.html', context)


def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Get all orders for this customer
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    # Get all installments for this customer
    installments = InstallmentPayment.objects.filter(customer=customer).order_by('order_item__order', 'month_number')
    
    context = {

        'customer': customer,
        'orders': orders,
        'installments': installments,
    }
    
    return render(request, 'customer_reports/customer_detail.html', context)


def get_order_guarantors(request, order_id):
    """AJAX view to get guarantors for a specific order"""
    order = get_object_or_404(Order, id=order_id)
    guarantors = order.guarantors.all()
    
    return render(request, 'customer_reports/guarantors_modal.html', {
        'guarantors': guarantors,
    })


def get_order_installments(request, order_id):
    """AJAX view to get installments for a specific order"""
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    installments = InstallmentPayment.objects.filter(order_item__in=order_items).order_by('month_number')
    
    return render(request, 'customer_reports/installments_modal.html', {
        'installments': installments,
    })


def download_installments_csv(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    installments = InstallmentPayment.objects.filter(customer=customer)

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=" {customer.first_name} {customer.last_name} installments.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order Item', 'Month Number', 'Amount Due', 'Amount Paid', 'Status', 'Due Date'])

    for installment in installments:
        writer.writerow([
            installment.order_item.product.name,
            installment.month_number,
            installment.amount_due,
            installment.amount_paid,
            'Paid' if installment.is_paid else 'Unpaid',
            installment.due_date.strftime('%Y-%m-%d') if not installment.is_paid else 'Paid'
        ])

    return response


def get_installment(request, installment_id):
    """AJAX view to get installment details for a specific installment"""
    installment = get_object_or_404(InstallmentPayment, id=installment_id)
    
    return render(request, 'customer_reports/update_installment_modal.html', {
        'installment': installment,
    })


def update_installment(request, installment_id):
    """View to update installment payment status"""
    installment = get_object_or_404(InstallmentPayment, id=installment_id)
    
    if request.method == 'POST':
        # Get form data
        from decimal import Decimal
        amount_paid = Decimal(request.POST.get('amount_paid', 0))
        
        # Update installment
        installment.amount_paid = amount_paid
        
        # is_paid will be automatically set in the save method if amount_paid >= initial_amount_due
        # Only force is_paid to True if explicitly marked as paid in the form
        if request.POST.get('is_paid') == 'True':
            installment.is_paid = True
            
        installment.save()
        
        # Update order's installment status
        order = installment.order_item.order
        order.update_installment_status()
        
        messages.success(request, f'Installment {installment.month_number} updated successfully.')
        
        # Always return JSON response to prevent redirect
        return JsonResponse({
            'success': True,
            'message': f'Installment {installment.month_number} updated successfully.'
        })
    
    return render(request, 'customer_reports/update_installment_modal.html', {
        'installment': installment,
    })