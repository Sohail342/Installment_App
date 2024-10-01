from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.CategoryListView.as_view(), name="category_list"),
     path('products/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:category_name>/', views.ProductListView.as_view(), name='products_list')
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
