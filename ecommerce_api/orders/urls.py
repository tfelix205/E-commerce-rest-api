from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderCancelView,
    OrderUpdateStatusView,
    OrderStatsView,
    UserOrderHistoryView
)

app_name = 'orders'

urlpatterns = [
    # Order endpoints
    path('', OrderListCreateView.as_view(), name='order_list'),
    path('history/', UserOrderHistoryView.as_view(), name='order_history'),
    path('stats/', OrderStatsView.as_view(), name='irder_stats'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order_detils'),
    path('<str:order_number>/cancel/', OrderCancelView.as_view(), name='order_cancel'),
    path('<str:order_number>/status/', OrderUpdateStatusView.as_view(), name='order_update_staus'),
]
