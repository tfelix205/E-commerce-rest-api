from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Payment, OrderStatusHistory


# Register your models here.
class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price', 'created_at')
    fields = ('product', 'product_name', 'price', 'quantity', 'total_price')
    
    
class PaymentInline(admin.StackedInline):
    """Inline admin for payment"""
    model = Payment
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fields = (
        'payment_method', 'status', 'amount', 'transaction_id', 'payment_intent_id', 'created_at', 'completed_at'
    )
    
    
class OrderStatusHistoryInline(admin.TabularInline):
    """Inline admin for order status history"""
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('status', 'note', 'created_by', 'created_at')
    
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for order model"""
    list_display = (
        'order_number', 'user_email', 'status_badge', 'payment_status_badge', 'total', 'total_items', 'created_at'
    )
    list_filter = (
        'order_number', 'user__email', 'user__first_name', 'user__last_name', 'shipping_full_name'
    )
    readonly_fields = (
        'order_number', 'total_items', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'
    )
    inlines = [OrderItemInline, PaymentInline, OrderStatusHistoryInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number', 'user', 'status', 'payment_status', 'created_at', 'updated_at'
            )
        }),
        ('Pricing', {
            'fields': (
                'subtotal', 'tax', 'shipping_cost', 'discount', 'total'
            )
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_full_name', 'shipping_phone',
                'shipping_address_line1', 'shipping_address_line2',
                'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Notes', {
            'fields': ('customer_note', 'admin_note')
        }),
        ('Timestamps', {
            'fields': ('paid_at', 'shipped_at', 'delivered_at')
        }),
    )
    
    def user_email(self, obj):
        """Display user email"""
        return obj.user.email
    user_email.short_description = 'User'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#FFA500',
            'proccessing': '#2196F3',
            'shipped': '#9c27b0',
            'delivered': '#4caf50',
            'cancelled': '#f44336',
            'refunded': '#607d88',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white;'
            'padding: 3px 10px; border-radius: 3px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        """Display payment status with color badge"""
        colors = {
            'pending': '#ffa500',
            'paid': '#4caf50',
            'failed': '#f44336',
            'refunded': '#607d8b',
        }
        color = colors.get(obj.payment_status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white;''padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model"""
    list_display = (
        'order', 'product_name', 'price', 'quantity', 'total_price', 'created_at'
    )
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product_name')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')
    
    
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model"""
    list_display = (
        'order', 'payment_method', 'status_badge', 'amount', 'transaction_id', 'created_at'
    )
    list_filter = ('paymnet_method', 'status', 'created_at')
    search_fields = (
        'order__order_number', 'transaction_id', 'payment_intent_id'
    )
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#ffa500',
            'completed': '#4caf50',
            'failed': '#f44336',
            'refunded': '#607d8b',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color:white;''padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')
    
    
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for OrderStatusHistory model"""
    list_display = ('order', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'note')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'created_by')

