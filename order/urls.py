from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('checkout/<int:user_id>/', views.checkout, name='checkout'),
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),
    
]
