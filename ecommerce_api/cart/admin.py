from django.contrib import admin
from .models import Cart, CartItem


# Register your models here.
class CartItemInline(admin.TabularInline):
    """Inline admin for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    fields = ('product', 'quantity', 'total_price', 'created_at')
    
    
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for cart model"""
    list_display = ('user', 'total_items', 'total', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('total_items', 'subtotal', 'total', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for cartItem model"""
    list_display = ('cart', 'product', 'quantity', 'total_price', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('cart__user__email', 'product__name')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cart__user', 'product')
    