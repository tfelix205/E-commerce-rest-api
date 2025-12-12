from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission class for admin users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin
    
    
class IsCustomer(permissions.BasePermission):
    """Permission class for customer users"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_customer
    
    
class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission class to allow owners or admin to edit"""
    
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_admin:
            return True
        # User can only access their own data
        return obj == request.user