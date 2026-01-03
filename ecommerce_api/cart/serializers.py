from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart item"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'product', 'product_id', 'quantity',
            'total_price', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
        
    def validate_product_id(self, value):
        """Validate product exixts and is active"""
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.in_stock:
                raise serializers.ValidationError("Product is out of stock")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least one")
        return value
    
    def validate(self, attrs):
        """Validate stock availability"""
        from products.models import Product
        
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
            if product.stock < quantity:
                raise serializers.ValidationError({
                    'quantity': f"Only {product.stock} units available"
                })
        except Product.DoesNotExist:
            pass   # Already handled in validate_product_id
        
        return attrs
    

class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating cart items"""
    product_id = serializers.IntegerField()
    
    class Meta:
        model = CartItem
        fields = ('product_id', 'quantity')
        
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        from products.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.in_stock:
                raise serializers.ValidationError("Product is out of stock")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
    
    def validate(self, attrs):
        """Validate stock availability"""
        from products.models import Product
        
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity', 1)
        
        product = Product.objects.get(id=product_id)
        
        # Check if updating existing cart item
        if self.instance:
            if product.stock < quantity:
                raise serializers.ValidationError({
                    'quantity': f"Only {product.stock} units available"
                })
        else:
            # Check for new cart item
            if product.stock < quantity:
                raise serializers.ValidationError({
                    'quantity': f"Only {product.stock} units available"
                })
        return attrs


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Cart
        fields = (
            'id', 'user', 'items', 'total_items', 'subtotal', 'total', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')