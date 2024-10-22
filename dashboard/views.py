from django.shortcuts import render
import json
from collections import defaultdict
from django.db.models import Sum
from products.models import Product
from order.models import Order, InstallmentPayment, OrderItem
from account.models import Customer
from django.db import connection
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='account:signin')
def dashboard(request):
    total_customers = Customer.objects.all().count()
    total_orders = Order.objects.all().count()
    installment_paid = InstallmentPayment.objects.filter(is_paid=True).count()
    installments_unpaid = InstallmentPayment.objects.filter(is_paid=False).count()


    '''Most Ordered Products'''

    top_ordered_items = (
        OrderItem.objects
        .values('product')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10] 
    )
    top_ordered_products = []
    for item in top_ordered_items:
        product = Product.objects.get(id=item['product'])
        top_ordered_products.append({
            'product': product,
            'total_quantity': item['total_quantity'],
            'id':product.id,
        })
        



    '''Instalment details for each product'''

    stats = defaultdict(lambda: {
        'total_installments': 0,
        'paid_installments': 0,
        'unpaid_installments': 0,
    })
    
    order_items = OrderItem.objects.prefetch_related('installments').all()

    for item in order_items:
        total_installments = item.installments.count()
        paid_installments = item.installments.filter(is_paid=True).count()
        unpaid_installments = total_installments - paid_installments

        # Aggregate data for each product
        stats[item.product.name]['total_installments'] += total_installments
        stats[item.product.name]['paid_installments'] += paid_installments
        stats[item.product.name]['unpaid_installments'] += unpaid_installments

    # Prepare the final list 
    final_stats = [
        {
            'product_name': product_name,
            **values
        }
        for product_name, values in stats.items()
    ]

    # State boxs
    stats_figures = [
        {
            'title': 'Total Orders',
            'figure': total_orders,
            'meta': '20%',
            'icon': 'bi-arrow-up',
            'meta_class': 'text-success',
        },
        {
            'title': 'Total Customers',
            'figure': total_customers,
            'meta': '5%',
            'icon': 'bi-arrow-down',
            'meta_class': 'text-success',
        },
        {
            'title': 'Projects',
            'figure': 23,  
            'meta': 'Open',
        },
        {
            'title': 'Invoices',
            'figure': 6,  
            'meta': 'New',
        },
        {
            'title': 'Unpiad Installments',
            'figure': installments_unpaid, 
            'meta': '',
        },
        {
            'title': 'Paid Installments',
            'figure': installment_paid,
            'meta': 'New',
        },
    ]


    context = {
        'stats_figures': stats_figures,
        'stats':final_stats,
        'top_ordered_products': top_ordered_products,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
    



@login_required(login_url='account:signin')
def order_view(request):
    
    return render(request, 'dashboard/orders.html',{'query_set':"hi"})


# # Raw SQl Query
# def fetch_company_details():
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             SELECT c.company_name, c.location, cl.company_clients
#             FROM core_company c
#             JOIN core_client cl ON c.id = cl.company_id
#         """)
#         rows = cursor.fetchall()
#         return rows



