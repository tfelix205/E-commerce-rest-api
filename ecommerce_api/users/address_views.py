from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Address
from .address_serializers import AddressSerializer, AddressCreateUpdateSerializer


class AddressListCreateView(generics.ListCreateAPIView):
    """List user addresses or create new address"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddressCreateUpdateSerializer
        return AddressSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an address"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AddressCreateUpdateSerializer
        return AddressSerializer
    
    def perform_destroy(self, instance):
        # soft delete
        instance.is_active = False
        instance.save()