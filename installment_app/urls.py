
from django.contrib import admin
from django.urls import path, include
from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('cart/', include('cart.urls')),
    path('', include("products.urls")),
    path('order/', include('order.urls')),
]
