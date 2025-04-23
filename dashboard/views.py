from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
import json
from django.db.models import Sum, Count
from products.models import Product, Category
from order.models import Order, InstallmentPayment, OrderItem
from account.models import Customer
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

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

@login_required(login_url='account:signin')
def inventory(request):
    categories = Category.objects.all().order_by('name')
    total_products = Product.objects.count()
    
    # Get data for inventory chart
    category_names = []
    product_counts = []
    in_stock_counts = []
    out_of_stock_counts = []
    
    for category in categories:
        category_names.append(category.name)
        category_products = Product.objects.filter(category=category)
        product_counts.append(category_products.count())
        
    
    context = {
        'categories': categories,
        'category_names': json.dumps(category_names),
        'product_counts': json.dumps(product_counts),
    }
    
    return render(request, 'dashboard/inventory.html', context)


@login_required(login_url='account:signin')
def category_products(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    # Get filter and sort parameters
    search_query = request.GET.get('search', '')
    sort_param = request.GET.get('sort', 'name')
    filter_param = request.GET.get('filter', 'all')
    
    # Base queryset
    products = Product.objects.filter(category=category)
    
    # Apply search filter
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Apply inventory filter
    if filter_param == 'in_stock':
        products = products.filter(inventory__gt=0)
    elif filter_param == 'out_of_stock':
        products = products.filter(inventory=0)
    elif filter_param == 'low_stock':
        products = products.filter(inventory__gt=0, inventory__lt=5)
    
    # Apply sorting
    products = products.order_by(sort_param)
    
    # Count statistics
    in_stock_count = products.filter(inventory__gt=0).count()
    out_of_stock_count = products.filter(inventory=0).count()
    
    context = {
        'category': category,
        'products': products,
        'in_stock_count': in_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'search_query': search_query,
        'sort': sort_param,
        'filter': filter_param
    }
    
    return render(request, 'dashboard/category_products.html', context)

@login_required(login_url='account:signin')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        photo = request.FILES.get('photo')
        
        if name and photo:
            category = Category(name=name, photo=photo)
            category.save()
            return redirect('dashboard:inventory')
    
    return render(request, 'dashboard/add_category.html')

@login_required(login_url='account:signin')
def add_product(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        price = request.POST.get('price')
        inventory = request.POST.get('inventory')
        details = request.POST.get('details')
        photo = request.FILES.get('photo')
        
        
        if name and price and inventory and details and photo:
            product = Product(
                name=name,
                price=price,
                inventory=inventory,
                details=details,
                photo=photo,
                category=category,
            )
            product.save()
            return redirect('dashboard:category_products', category_slug=category.slug)
    
    context = {
        'category': category
    }
    
    return render(request, 'dashboard/add_product.html', context)

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
