from django.urls import path
from . import views

app_name = 'customer_reports'

urlpatterns = [
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('download_installments/<int:customer_id>/', views.download_installments_csv, name='download_installments'),
    path('order_summary/<int:order_id>/', views.order_summary, name="order_summary"),
    path('order_guarantors/<int:order_id>/', views.get_order_guarantors, name="order_guarantors"),
    path('order_installments/<int:order_id>/', views.get_order_installments, name="order_installments"),
    path('update_installment/<int:installment_id>/', views.update_installment, name="update_installment"),
    path('get_installment/<int:installment_id>/', views.get_installment, name="get_installment")
]
    
