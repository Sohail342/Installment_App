from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Category, Product
from django.db.models import Q 
from django.http import JsonResponse
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



def filter_categories(request):
    query = request.GET.get('filter', '').strip()
    print(query)
    
    if query:  # Only perform the search if query is not empty
        categories = Category.objects.filter(name__icontains=query).values('name', 'id')[:6]
    else:
        categories = Category.objects.none()  # Return an empty queryset if no query
    
    results = [
        {'name': category['name'], 'url': reverse('products:products_list', args=[category['name']])}
        for category in categories
    ]
    
    return JsonResponse(results, safe=False)



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

        dynamic_installment = product.calculate_dynamic_installment_plan(user_down_payment, user_months)


        # Store data in session
        request.session['down_payment'] = dynamic_installment['down_payment']
        request.session['installment_plan'] = dynamic_installment['installment_plan']
        request.session['monthly_payment'] = dynamic_installment['monthly_payment']
        request.session['total_amount'] = dynamic_installment['total_amount']
        request.session['product'] = product.inventory
        request.session['product_id'] = product.pk

        return redirect(reverse('order:dynamic_installment_details'))
    
    return render(request, 'products/product_details.html', {
        'product': product, 
        'installments': installments['installments'],
        'down_payments': installments['down_payments'],
        'total_amounts': installments['total_amounts'],
        'months': months,
        'quantity': product.inventory,
    })
