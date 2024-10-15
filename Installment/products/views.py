from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Category, Product
from django.db.models import Q 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404


@login_required(login_url='account:signin')
def category_list_view(request):
    query = request.GET.get('search', '')
    clean_query = query.strip()

    if clean_query:
        categories = Category.objects.filter(name__icontains=clean_query).order_by('name')
    else:
        categories = Category.objects.all().order_by('name')

    # Set up pagination
    paginator = Paginator(categories, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/category_list.html', {'categories': page_obj})



@login_required(login_url='account:signin') 
def product_list_view(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    
    # Get the search query
    query = request.GET.get('search', '')
    clean_query = query.strip()

    # Filter products by name if there's a search query
    if clean_query:
        products = Product.objects.filter(category=category).filter(Q(name__icontains=clean_query)).order_by('name')
    else:
        products = Product.objects.filter(category=category).order_by('name')

    # Set up pagination
    paginator = Paginator(products, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/category_products.html', {
        'products': page_obj,
        'category': category,
        'search_query': clean_query,
    })



@login_required(login_url='account:signin')
def product_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    months = [month for month in range(1, 13)]
    installments = product.get_installment_plan()


    #  dynamic Installments
    if request.method == "POST":
        user_down_payment = request.POST.get('user_down_payment')
        user_months = request.POST.get('user_months')

        dynamic_installment = product.calculate_dynamic_installment_plan(user_down_payment=user_down_payment, user_months=user_months)

        print(dynamic_installment)
    
    return render(request, 'products/product_details.html', {
        'product': product, 
        'installments': installments['installments'],
        'down_payments': installments['down_payments'],
        'total_amounts': installments['total_amounts'],
        'months': months,
        'quantity': product.inventory,
    })
