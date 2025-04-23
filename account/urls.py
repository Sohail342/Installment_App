from django.urls import path
from . import views
from . import api

app_name = 'account'

urlpatterns = [
    path('signin/', views.login_view, name='signin'),
    path('logout/', views.signout, name="signout"),
     path('customer/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),
    path('api/customer-search/', api.customer_search, name='customer_search'),
]