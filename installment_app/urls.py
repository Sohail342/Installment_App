
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include("account.urls")),
    path('cart/', include('cart.urls')),
    path('', include("products.urls")),
]
