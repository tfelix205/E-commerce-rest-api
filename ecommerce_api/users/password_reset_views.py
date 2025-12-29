from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .email_utils import send_password_reset_email, verify_token
from .serializers import ChangePasswordSerializer

User = get_user_model()


class RequestPasswordResetView(APIView):
    """Request password reset email"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            user = User.objects.get(email=email, is_active=True)
            send_password_reset_email(user, request)
            
            return Response(
                {'message': 'Password reset email has been sent'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response(
                {'message': 'If an account exists with this email, a password reset link has been sent'},
                status=status.HTTP_200_OK
            )
            
            
class PasswordResetConfirmView(APIView):
    """Reset password using token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, uidb64, token):
        user = verify_token(uidb64, token)
        
        if user is None:
            return Response(
                {'error': 'Invalid or expire token'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        new_password = request.data.get('new_password')
        new_password2 = request.data.get('new_password2')
            
        if not new_password or not new_password2:
            return Response(
                {'error': 'Both password fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if new_password != new_password2:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Validate password strength
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'error': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'message': 'Password has been reset successfully'},
            status=status.HTTP_200_OK
        )
        
        
class EmailVerificationView(APIView):
    """Verify user email"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, uidb64, token):
        user = verify_token(uidb64, token)
        
        if user is None:
            return Response(
                {'error': 'Invalid or expired verification link'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if user.is_email_verified:
            return Response(
                {'message': 'Email already verified'},
                status=status.HTTP_200_OK
            )
            
        user.is_email_verified = True
        user.save()
        
        return Response(
            {'message': 'Email verified successfully'},
            status=status.HTTP_200_OK
        )
        

class ResendVerificationEmailView(APIView):
    """Resend verification email"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        if user.is_email_verified:
            return Response(
                {'message': 'Email is already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from .email_utils import send_verification_email
        send_verification_email(user, request)
        
        return Response(
            {'message': 'Verification email has been sent'},
            status=status.HTTP_200_OK
        )