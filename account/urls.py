from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('signin/', views.login_view, name='signin'),
    path('logout/', views.signout, name="signout"),
     path('customer/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),
]