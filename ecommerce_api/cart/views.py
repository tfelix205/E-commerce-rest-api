from django.shortcuts import render
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem
from products.models import Product
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    CartItemCreateUpdateSerializer
)


# Create your views here.
class CartView(APIView):
    """View for getting user's cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CartItemAddView(APIView):
    """Add item to cart or update quantity if exists"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """Add items to cart"""
        serializer = CartItemCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Get product
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            # Check if item already in cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                # Update quantity if item already exists
                new_quantity = cart_item.quantity + quantity
                
                # Validate stock
                if product.stock < new_quantity:
                    return Response(
                        {'error': f'Only {product.stock} units available'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                cart_item.quantity = new_quantity
                cart_item.save()
                
            # Return updated cart
            cart_serializer = CartSerializer(cart)
            return Response(
                cart_serializer.data,
                status=status.HTTP_201_CREATED if item_created else status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CartItemUpdateView(APIView):
    """Update cart item quantity"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def patch(self, request, item_id):
        """Update cart item quantity"""
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        serializer = CartItemCreateUpdateSerializer(
            cart_item,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            quantity = serializer.validated_data.get('quantity', cart_item.quantity)
            
            # Validate stock
            if cart_item.product.stock < quantity:
                return Response(
                    {'error': f'Only {cart_item.product.stock} units availale'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = quantity
            cart_item.save()
            
            # Return updated cart
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CartItemDeleteView(APIView):
    """Remove item from cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def delete(self, request, item_id):
        """Delete cart item"""
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        cart_item.delete()
        
        # Return updated cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    
class CartClearView(APIView):
    """Clear all items from cart"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def delete(self, request):
        """Clear cart"""
        cart = get_object_or_404(Cart, user=request.user)
        cart.clear()
        
        # Return empty cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    
class CartItemBulkUpdateView(APIView):
    """Bulk update cart items"""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def put(self, request):
        """
        Bulk update cart items
        Expected format: [{"product_id": 1, "quantity": 2}, ...]
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        items_data = request.data.get('items', [])
        
        if not isinstance(items_data, list):
            return Response(
                {'error': 'Items must be a list'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        errors = []
        updated_items = []
        
        for item_data in items_data:
            serializer = CartItemCreateUpdateSerializer(data=item_data)
            
            if serializer.is_valid():
                product_id = serializer.validated_data['product_id']
                quantity = serializer.validated_data['quantity']
                
                try:
                    product = Product.objects.get(id=product_id, is_active=True)
                    
                    if product.stock < quantity:
                        errors.append({
                            'product_id': product_id,
                            'error': f'Only {product.stock} units available'
                        })
                        continue
                    
                    cart_item, item_created = CartItem.objects.update_or_create(
                        cart=cart,
                        product=product,
                        defaults={'quantity': quantity}
                    )
                    updated_items.append(cart_item.id)
                    
                except Product.DoesNotExist:
                    errors.append({
                        'product_id': product_id,
                        'error': 'Product not found'
                    })
            else:
                errors.append({
                    'data': item_data,
                    'errors': serializer.errors
                })
                
        # Return updated cart with any errors
        cart_serializer = CartSerializer(cart)
        response_data = cart_serializer.data
        
        if errors:
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        return Response(response_data, status=status.HTTP_200_OK)

