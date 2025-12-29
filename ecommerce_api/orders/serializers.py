from rest_framework import serializers
from .models import Order, OrderItem, Payment, OrderStatusHistory
from users.address_serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order item"""
    
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'product_name', 'product_sku', 'price', 'quantity', 'total_price', 'created_at'
        )
        read_only_fields = ('id', 'total_price', 'created_at')
        
        
class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment"""
    
    class Meta:
        model = Payment
        fields = (
            'id', 'payment_method', 'status', 'transaction_id', 'payment_intent_id', 'amount', 'created_at',
            'completed_at'
        )
        read_only_fields = (
            'id', 'status', 'transaction_id', 'payment_intent_id', 'created_at', 'completed_at', 'completed_at'
        )
        
    
class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for order status history"""
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ('id', 'status', 'note', 'created_by_email', 'created_at')
        read_only_fields = ('id', 'created_at')
        
        
class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view"""
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'payment_status', 'total', 'total_items', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'order_number', 'created_at', 'updated_at')
        

class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for order detail view"""
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'status', 'payment_status', 'subtotal', 'tax', 'shipping_cost', 'discount',
            'total', 'shipping_full_name', 'shipping_phone', 'shipping_address_line1', 'shipping_address_line2',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country', 'customer_note',
            'admin_note', 'items', 'payment', 'total_items', 'status_history',
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at' 
        )
        read_only_fields = (
            'id', 'order_number', 'user', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'
        )
        

class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=['stripe', 'paypal', 'cash']
    )
    customer_note = serializers.CharField(required=False, allow_blank=True)
    
    def validate_shipping_address_id(self, value):
        """Validate shipping address exists and belongs to user"""
        from users.models import Address
        request = self.context.get('request')
        
        if not Address.objects.filter(
            id=value,
            user=request.user,
            is_active=True
        ).exists():
            raise serializers.ValidationError("Invalid shipping address")
        return value
        
        
class OrderUpdateStatusSerializer(serializers.Serializer):
    """Serializer for updating order status"""
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
            ('refunded', 'Refunded'),
        ]
    )
    note = serializers.CharField(required=False, allow_blank=True)
    
    
class OrderCancelSerializer(serializers.Serializer):
    """Serializer for cancelling orders"""
    reason = serializers.CharField(required=False, allow_blank=True)