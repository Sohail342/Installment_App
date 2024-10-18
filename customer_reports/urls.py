from django.urls import path
from . import views

app_name = 'customer_reports'

urlpatterns = [

    path('download_installments/<int:customer_id>/', views.download_installments_csv, name='download_installments'),
    path('order_summary/<int:order_id>/', views.order_summary, name="order_summary")
]
    
