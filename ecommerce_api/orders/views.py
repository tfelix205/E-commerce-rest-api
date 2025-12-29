from django.shortcuts import render
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderItem, Payment, OrderStatusHistory
from cart.models import Cart
from users.models import Address
from products.models import Product
from users.permissions import IsAdmin
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderUpdateStatusSerializer,
    OrderCancelSerializer
)


# Create your views here.
class OrderListCreateView(generics.ListCreateAPIView):
    """List user's orders or create new order fro cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Order.objects.all().select_related('user', 'payment')
        return Order.objects.filter(user=user).select_related('payment')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create order from cart"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
            # check id cart has items
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
                # Validate stock for all items
                for cart_item in cart.items.all():
                    if cart_item.product.stock < cart_item.quantity:
                        return Response(
                            {
                                'error': f'Insufficient stock for {cart_item.product.name}.'
                                f'Only {cart_item.product.stock} available.'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Get shipping address
                shipping_address = get_object_or_404(
                    Address,
                    id=serializer.validated_data['shipping_address_id'],
                    user=request.user
                )
                
                # Calculate totals
                subtotal = cart.subtotal
                tax = subtotal * 0.1  # 10% tax
                shipping_cost = 10.00 if subtotal < 100 else 0   # free shipping for over $100
                discount = 0
                total = subtotal + tax + shipping_cost - discount
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    status='pending',
                    subtotal=subtotal,
                    payment_status='pending',
                    tax=tax,
                    shipping_cost=shipping_cost,
                    discount=discount,
                    total=total,
                    shipping_address=shipping_address,
                    shipping_full_name=shipping_address.fullname,
                    shipping_phone=shipping_address.phone,
                    shipping_address_line1=shipping_address.adress_line1,
                    shipping_address_line2=shipping_address.address_line2,
                    shipping_city=shipping_address.city,
                    shipping_state=shipping_address.state,
                    shipping_postal_code=shipping_address.postal_code,
                    shipping_country=shipping_address.country,
                    customer_note=serializer.validated_data.get('customer_note', '')
                )
                
                # Create order items from cart items
                for cart_item in cart.tems.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        product_name=cart_item.product_name,
                        product_sku='',
                        price=cart_item.product.price,
                        quantity=cart_item.quantity
                    )
                    
                    # Reduce product stock
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()
                    
                    # Create payment record
                    Payment.objects.create(
                        order=order,
                        payment_method=serializer.validated_data['payment_method'],
                        amount=total,
                        status='pending'
                    )
                    
                    # Create initial status history
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='pending',
                        note='Order created',
                        created_by=request.user
                    )
                    
                    # Clear cart
                    cart.clear()
                    
                    # Return created order
                    order_serializer = OrderDetailSerializer(order)
                    return Response(
                        order_serializer.data,
                        status=status.HTTP_201_CREATED
                    )


class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve order details"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer
    lookup_field = 'order-number'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    
class OrderCancelView(APIView):
    """Cancel an order"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, order_number):
        """Cancel order"""
        # Get order
        if request.user.is_admin:
            order = get_object_or_404(Order, oerder_number=order_number)
        else:
            order = get_object_or_404(
                Order,
                order_number=order_number,
                user=request.user
            )
            
        # Check if order can be cancelled
        if not order.can_cancel():
            return Response(
                {'error': f'Order cannot be cancelled. Current status: {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = OrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Restore product stock
        
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
                
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='cancelled',
            note=serializer.validated_data.get('reason', 'Order cancelled by customer'),
            created_by=request.user
        )
        
        # Return updated order
        order_serializer = OrderDetailSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_200_OK)
    
    
class OrderUpdateStatusView(APIView):
    """Update order status (Admin only)"""
    permission_classes = [IsAdmin]
    
    @transaction.atomic
    def patch(self, request, order_number):
        """Update order status"""
        order = get_object_or_404(Order, order_number=order_number)
        
        serializer = OrderUpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_status = serializer.validated_data['status']
        note = serializer.validated_data.get('note', '')
        
        # Update order status
        old_status = order.status
        order.status = new_status
        
        # Update timestamps based on status
        if new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
            
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            note=note or f'Status changed from {old_status} to {new_status}',
            created_by=request.user
        )
        
        # Return updated order
        order_serializer = OrderDetailSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_200_OK)
    
    
class OrderStatsView(APIView):
    """Get order statistics (Admin only)"""
    permission_classes = [IsAdmin]
    
    def get(self, request):
        """get order statistics"""
        from django.db.models import Count, Sum, Avg
        
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0
        
        orders_by_status = Order.objects.values('status').annotate(
            count=Count('id')
        )
        
        average_order_value = Order.objects.filter(
            payment_status='paid'
        ).aggregate(avg=Avg('total'))['avg'] or 0
        
        recent_orders = Order.objects.all()[:10]
        recent_orders_data = OrderListSerializer(recent_orders, many=True).data
        
        return Response({
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'average_order_value': float(average_order_value),
            'orders_by_status': list(orders_by_status),
            'recent_orders': recent_orders_data
        })
        
        
class UserOrderHistoryView(generics.ListAPIView):
    """Get user's order history"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderListSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')