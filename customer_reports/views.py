import csv
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from order.models import InstallmentPayment
from account.models import Customer
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