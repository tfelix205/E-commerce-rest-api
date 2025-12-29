from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    ProductListCreateView,
    ProductDetailView,
    ProductSearchView,
    FeaturedProductsView,
    ProductImageUploadView,
    ReviewListCreateView,
    ReviewDetailView
)


app_name = 'products'


urlpatterns = [
    # Category endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # Product endpoints
    path('', ProductListCreateView.as_view(), name='product_list'),
    path('featured/', FeaturedProductsView.as_view(), name='featured_products'),
    path('search/', ProductSearchView.as_view(), name='product_search'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Product image upload
    path('<int:product_id>/images/', ProductImageUploadView.as_view(), name='product_image_upload'),
    
    # Review endpoints
    path('<int:product_id>/reviews/', ReviewListCreateView.as_view(), name='review_list'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review_detail')
]