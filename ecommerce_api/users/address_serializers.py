from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for Address Model"""
    
    class Meta:
        model = Address
        fields = (
            'id', 'user', 'address_type', 'full_name', 'phone',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'is_default', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
        
    def validate_phone(self, value):
        """Validate phone number"""
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits")
        return value
    
    def validate_postal_code(self, value):
        """Validate postal code"""
        if not value:
            raise serializers.ValidationError("Postal code is required")
        return value
    
    
class AddressCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating address"""
    
    class Meta:
        model = Address
        fields = (
            'address_type', 'full_name', 'phone', 'address_line1',
            'address_line2', 'city', 'state', 'postal_code',
            'country', 'is_default'
        )