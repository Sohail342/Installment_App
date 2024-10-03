from django.shortcuts import render
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from .models import Category, Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404

@login_required(login_url='account:signin')
def category_list_view(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'products/category_list.html', context)



class ProductListView(LoginRequiredMixin, ListView):
    login_url = 'account:signin'  # Redirect to login page if not logged in
    redirect_field_name = 'next'  # After login, redirect back to this view
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_name = self.kwargs['category_name']
        category = get_object_or_404(Category, name=category_name)
        return Product.objects.filter(category=category)



class ProductDetailView(LoginRequiredMixin, View):
    login_url = 'account:signin'  # Redirect to login page if not logged in
    redirect_field_name = 'next'  # After login, redirect back to this view

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        months = [months for months in range(1, 13)]
        installments = product.get_installment_plan()
        
        return render(request, 'products/product_details.html', {
            'product': product, 
            'installments': installments['installments'],
            'down_payments': installments['down_payments'],
            'total_amounts': installments['total_amounts'],
            'months': months,
            'quantity': product.inventory,
        })
