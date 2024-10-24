from django.shortcuts import render
from collections import defaultdict
import json
from django.db.models import Sum, Count
from products.models import Product, Category
from order.models import Order, InstallmentPayment, OrderItem
from account.models import Customer
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib.auth.decorators import login_required

@login_required(login_url='account:signin')
def dashboard(request):
    context = {
        'stats_figures': get_stats_figures(),
        'stats': get_product_installment_stats(),
        'top_ordered_products': get_top_ordered_products(),
        'order_counts': json.dumps(get_monthly_order_counts()[1]),
        'months': json.dumps(get_monthly_order_counts()[0]),
        'current_year': get_monthly_order_counts()[2],
        'top_categories':get_top_categories()[0],
        'order_quantities_for_categories':get_top_categories()[1]
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def get_stats_figures():
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()
    total_paid_orders = Order.objects.filter(is_paid=True).count()
    total_unpaid_orders = Order.objects.filter(is_paid=False).count()
    installment_paid = InstallmentPayment.objects.filter(is_paid=True).count()
    installments_unpaid = InstallmentPayment.objects.filter(is_paid=False).count()

    return [
        {
            'title': 'Total Orders',
            'figure': total_orders,
            'meta_class': 'text-success',
        },
        {
            'title': 'Total Customers',
            'figure': total_customers,
            'meta_class': 'text-success',
        },
        {
            'title': 'Unpaid Orders',
            'figure': total_unpaid_orders,  
        },
        {
            'title': 'Paid Orders',
            'figure': total_paid_orders,  
        },
        {
            'title': 'Unpaid Installments',
            'figure': installments_unpaid, 
            'meta': 'Unpaid',
            'meta_class': 'text-danger',
        },
        {
            'title': 'Paid Installments',
            'figure': installment_paid,
            'meta': 'Paid',
            'meta_class': 'text-success',
        },
    ]


def get_top_categories():
    # Get the top 5 categories with the most associated orders
    top_categories = (
        Category.objects.annotate(
            total_orders=Count('product__orderitem__order')
        )
        .order_by('-total_orders')[:5]
    )

    # Extract category names and their order quantities
    category_names = [category.name for category in top_categories]
    order_quantities = [category.total_orders for category in top_categories]

    return category_names, order_quantities



def get_monthly_order_counts():
    now = timezone.now()
    current_year = now.year
    year_start = now.replace(month=1, day=1)
    current_month_end = (now.replace(day=1) + timezone.timedelta(days=31)).replace(day=1) - timezone.timedelta(days=1)

    monthly_orders = (
        Order.objects
        .filter(created_at__range=(year_start, current_month_end))
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(order_count=Count('id'))
        .order_by('month')
    )

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    order_counts = [0] * 12

    for order in monthly_orders:
        month_index = order['month'].month - 1
        order_counts[month_index] = order['order_count']

    return months[:now.month], order_counts[:now.month], current_year


def get_top_ordered_products():
    top_ordered_items = (
        OrderItem.objects
        .values('product')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]
    )

    return [
        {
            'product': Product.objects.get(id=item['product']),
            'total_quantity': item['total_quantity'],
            'id': item['product'],
        }
        for item in top_ordered_items
    ]


def get_product_installment_stats():
    stats = defaultdict(lambda: {
        'total_installments': 0,
        'paid_installments': 0,
        'unpaid_installments': 0,
        'id': None
    })
    
    order_items = OrderItem.objects.prefetch_related('installments').all()

    for item in order_items:
        total_installments = item.installments.count()
        paid_installments = item.installments.filter(is_paid=True).count()
        unpaid_installments = total_installments - paid_installments

        stats[item.product.name]['total_installments'] += total_installments
        stats[item.product.name]['paid_installments'] += paid_installments
        stats[item.product.name]['unpaid_installments'] += unpaid_installments
        stats[item.product.name]['id'] = item.product.id

    return [
        {'product_name': product_name, **values}
        for product_name, values in stats.items()
    ]



@login_required(login_url='account:signin')
def order_view(request):
    return render(request, 'dashboard/orders.html', {'query_set': "hi"})
