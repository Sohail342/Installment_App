import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from io import BytesIO
from django.shortcuts import get_object_or_404
from order.models import InstallmentPayment
from account.models import Customer

def download_installments_csv(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    installments = InstallmentPayment.objects.filter(customer=customer)

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="installments.csv"'

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




def download_installments_pdf(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    installments = InstallmentPayment.objects.filter(customer=customer)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{customer.first_name}_{customer.last_name}_installments.pdf"'
    
    # Create the PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add content to the PDF
    p.drawString(100, height - 50, f"Installments for {customer.first_name} {customer.last_name}")
    p.drawString(100, height - 70, f"Email: {customer.email}")
    p.drawString(100, height - 90, f"Phone Number: {customer.phone_number}")
    p.drawString(100, height - 110, f"Address: {customer.address}")
    p.drawString(100, height - 130, f"CNIC: {customer.cnic}")

    # Table header
    y = height - 160
    p.drawString(100, y, "Order Item")
    p.drawString(250, y, "Month Number")
    p.drawString(350, y, "Amount Due")
    p.drawString(450, y, "Amount Paid")
    p.drawString(550, y, "Status")
    p.drawString(650, y, "Due Date")
    
    y -= 20  # Move down for the data rows

    # Add rows
    for installment in installments:
        p.drawString(100, y, str(installment.order_item.product.name))
        p.drawString(250, y, str(installment.month_number))
        p.drawString(350, y, str(installment.amount_due))
        p.drawString(450, y, str(installment.amount_paid))
        p.drawString(550, y, 'Paid' if installment.is_paid else 'Unpaid')
        p.drawString(650, y, installment.due_date.strftime('%Y-%m-%d') if not installment.is_paid else 'Paid')
        y -= 20  # Move down for the next row

    p.showPage()
    p.save()

    # Return PDF response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response