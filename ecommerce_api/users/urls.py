from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .jwt_serializers import CustomTokenObtainPairView
from .views import (
    UserRegistrationView,
    UserProfileView,
    ChangePasswordView,
    LogoutView,
    UserListView,
    UserDetailView
)
from .password_reset_views import (
    RequestPasswordResetView,
    PasswordResetConfirmView,
    EmailVerificationView,
    ResendVerificationEmailView
)
from .address_views import AddressListCreateView, AddressDetailView

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Email Verification
    path('verify-email/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verificaion/', ResendVerificationEmailView.as_view(), name='resend_verification'),

    # Password reset
    path('resquest-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('reset-password/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Address endpoints
    path('addresses/', AddressListCreateView.as_view(), name='address_list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
  
    # Admin endpoints
    path('', UserListView.as_view(), name='user_list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user_detail')
    
]