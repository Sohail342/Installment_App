from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'products'

urlpatterns = [
    path('', views.category_list_view, name="category_list"),
    path('products/<int:product_id>/', views.product_detail_view, name='product_detail'),
    path('category/<str:category_name>/', views.product_list_view, name='products_list'),
     path('filter-categories/', views.filter_categories, name='filter_categories'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
