from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', views.order_view, name='orders'),
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('inventory/category/', views.add_category, name='add_category'),
    path('inventory/category/<slug:category_slug>/add-product/', views.add_product, name='add_product'),
]
