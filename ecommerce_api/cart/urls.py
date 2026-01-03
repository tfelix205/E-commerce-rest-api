from django.urls import path
from .views import (
    CartView,
    CartItemAddView,
    CartItemUpdateView,
    CartItemDeleteView,
    CartClearView,
    CartItemBulkUpdateView
)

app_name = 'cart'

urlpatterns = [
    # Cart endpoints
    path('', CartView.as_view(), name='cart'),
    path('add/', CartItemAddView.as_view(), name='cart_add'),
    path('clear/', CartClearView.as_view(), name='cart_clear'),
    path('bulk-update/', CartItemBulkUpdateView.as_view(), name='cart_bulk_update'),
    
    # Cart item endpoints
    path('items/<int:item_id>/', CartItemUpdateView.as_view(), name='cart_item_update'),
    path('items/<int:item_id>/delete/', CartItemDeleteView.as_view(), name='Cart_item_delete')
]
