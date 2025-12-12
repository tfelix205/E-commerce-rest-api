from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'role')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
        
    def validate(self, attrs):
        """Validate password match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        """Create and return a new user"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    
    
class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'is_active', 'date_joined'
        )
        read_only_fields = ('id', 'role', 'date_joined')
        

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')
     
        
class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate password match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidatorError(
                {"new_password": "password didn't match."}
            )
        return attrs
    
    
class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin to manage users"""
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'phone',
            'role', 'is_active', 'is_staff', 'date_joined', 'updated_at'
        )
        read_only_fields = ('id', 'date_joined', 'updated_at')
