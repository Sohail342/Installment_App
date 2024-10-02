from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .models import Category, Product
from django.shortcuts import render, get_object_or_404

class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all()



class ProductListView(ListView):
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'

    def get_queryset(self):
        category_name = self.kwargs['category_name']
        category = get_object_or_404(Category, name=category_name)
        return Product.objects.filter(category=category)



class ProductDetailView(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        
        months = [months for months in range(1, 13)]
        price = product.price  
        installments = {
            '3_months': int(price / 3)+150,
            '6_months': int(price / 6)+200,
            '9_months': int(price / 9)+350,
            '12_months': int(price / 12)+450,
        }
        
        return render(request, 'products/product_details.html', {
            'product': product, 
            'installments': installments,
            'months':months,
            })