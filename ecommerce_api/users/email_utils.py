from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string


def send_verification_email(user, request):
    """Send email verification to user"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Build verification url
    domain = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    verification_url = f"{protocol}://{domain}/api/users/verify-email/{uid}/{token}/"
    
    subject = 'Verify your email address'
    message = f"""
    Hi {user.first_name},
    Thank you for registering! Please verify your email address by clicking the link below:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    if you didn't create an account, please ignore this email.
    
    Best regards,
    E-Commerce Team
    """
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user, request):
    """Send password reset email to user"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Build reset URL
    domain = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    reset_url = f"{protocol}://{domain}/api/users/reset-password/{uid}/{token}/"
    
    subject = 'Password Reset Request'
    message = f"""
    Hi {user.first_name},
    you requested to reset your password. Click the link below to reset your password:
    
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request a password reset, please ignore this email.
    
    Best regards,
    E-commerce Team
    """
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
    

def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = 'Welcome to E-Commerce!'
    message = f"""
    Hi {user.first_name},
    
    Welcome to our E-Commerce platform! we're excited to have you on board.
    
    you can now:
    - Browse our products
    - Add items to your cart
    - Place orders
     leave reviews
     
     If you have any questions, feel free to contact our support team.
     
     Happy shopping!
     
     Best regards,
     E-Commerce Team
    """
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
    
    
def verify_token(uidb64, token):
    """Verify the token and return user"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    if default_token_generator.check_token(user, token):
        return user

    return None