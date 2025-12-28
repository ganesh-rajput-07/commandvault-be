from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (GoogleLoginView, UserProfileView, UserUpdateView, 
                    DeactivateAccountView, FollowUserView, UnfollowUserView, PublicUserProfileView,
                    VerifyEmailView, ResendVerificationView)
from .custom_auth import CustomLoginView, CustomRegisterView

urlpatterns = [
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('user/', UserUpdateView.as_view(), name='user-update'),  # Changed from profile/update/
    path('users/<str:username>/profile/', PublicUserProfileView.as_view(), name='public-user-profile'),
    path('deactivate/', DeactivateAccountView.as_view(), name='deactivate'),
    path('users/<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('users/<int:user_id>/unfollow/', UnfollowUserView.as_view(), name='unfollow-user'),
    # Email Verification
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
]
