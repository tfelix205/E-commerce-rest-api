from django.shortcuts import render
from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.db.models import Q, Avg
from users.permissions import IsAdmin
from .models import Category, Product, ProductImage, Review
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateUpdateSerializer,
    ProductImageSerializer,
    ReviewSerializer
)


class CategoryListCreateView(generics.ListCreateAPIView):
    """List all categories or create a new category"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        if self.request.methos == 'POST':
            return [IsAdmin()]
        return [permissions.AllowAny()]
    
    
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve update or delete a category"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        return [permissions.AllowAny()]
    
    
class ProductListCreateView(generics.ListCreateAPIView):
    """List all products or create a new product"""
    queryset = Product.objects.filter(is_active=True).select_related('category')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    serach_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.methos == 'POST':
            return ProductCreateUpdateSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by price range
        
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter by stock availability
        in_stock = self.request.query_paramas.get('in_stock')
        if in_stock and in_stock.lower() == 'True':
            queryset = queryset.filter(stock__gt=0)
        return queryset
    

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve update or delete a product"""
    queryset = Product.objects.all().select_related('category').prefetch_related('images', 'reviews')
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdmin()]
        return [permissions.AllowAny()]
    
    def retrieve(self, request, *args, **kwargs):
        """Overide to implement caching"""
        slug = kwargs.get('slug')
        cache_key = f'product_{slug}'
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # If not cache, get from database
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        #Cache for 15 minutes
        cache.set(cache_key, serializer.data, 60 * 15)
        
        return Response(serializer.data)
    

class ProductSearchView(APIView):
    """Advanced product search"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontins=query) |
            Q(category__name__icontains=query),
            is_active=True
        ).select_related('category')[:20]
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    
class FeaturedProductsView(generics.ListAPIView):
    """List featured products"""
    queryset = Product.objects.filter(is_active=True, is_featured=True).select_related('category')
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    
    
class ProductImageUploadView(APIView):
    """Upload additional product images"""
    permission_classes = [IsAdmin]
    
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )        
            
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ReviewListCreateView(generics.ListCreateAPIView):
    """List reviews for a product or create a new review"""
    serializer_class = ReviewSerializer
        
    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id)
        
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
        
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_id')
        serializer.save(user=self.request.user, product_id=product_id)
            
            
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a review"""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    def get_permissions(self):
        if self.rquest.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_object(self):
        obj = super().get_object()
        
        # Only review owner or admin can update/delete
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != self.request.user and not self.request.user.is_admin:
                self.permission_denied(self.request)
        
        return obj