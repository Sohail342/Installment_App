from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_page, name='view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('clear_cart/<int:product_id>/', views.clear_cart, name='clear_cart'),
    path('clear_all/', views.clear_all_cart, name='clear_all'),
]
