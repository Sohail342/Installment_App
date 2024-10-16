from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('checkout/<int:user_id>/', views.checkout, name='checkout'),
    path('order-summary/<int:order_id>/', views.order_summary, name='order_summary'),
    path('total_bill/', views.total_bill_view, name='total_bill'),
    path("installment_details/", views.dynamic_installment_details, name='dynamic_installment_details')
    
]
