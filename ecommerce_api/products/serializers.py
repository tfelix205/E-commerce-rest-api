from rest_framework import serializers
from .models import Category, Product, ProductImage, Review


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'is_active', 'product_count', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at', 'product_count')
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    
    
class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model"""
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'created_at')
        read_only_fields = ('id', 'created_at')
        
        
class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for review model"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Review
        fields = (
            'id', 'product', 'user', 'user_name', 'user_email',
            'rating', 'comment', 'is_verified', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'is_verified', 'created_at', 'updated_at')
        
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'category', 'category_name',
            'price', 'stock', 'stock_status', 'in_stock', 'image',
            'is_active', 'is_featured', 'average_rating', 'review_count', 'created_at',
        )
        read_only_fields = ('id', 'slug', 'stock_status', 'in_stock', 'created_at')
        
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    
class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for Product detail view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'category', 'category_name',
            'price', 'stock', 'stock_status', 'in_stock', 'image', 'images',
            'is_active', 'is_featured', 'average_rating', 'review_count', 'reviews',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'stock_status', 'in_stock', 'created_at', 'updated_at')
        
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    
class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating product"""
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'category', 'price',
            'stock', 'image', 'is_active', 'is_featured'
        )
        read_only_fields = ('id',)
        
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("stock cannot be negative")
        return value