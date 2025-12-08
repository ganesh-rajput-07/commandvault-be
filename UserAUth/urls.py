from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (RegisterView, GoogleLoginView, UserProfileView, UserUpdateView, 
                    DeactivateAccountView, FollowUserView, UnfollowUserView, PublicUserProfileView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('user/', UserUpdateView.as_view(), name='user-update'),  # Changed from profile/update/
    path('users/<int:pk>/profile/', PublicUserProfileView.as_view(), name='public-user-profile'),
    path('deactivate/', DeactivateAccountView.as_view(), name='deactivate'),
    path('users/<int:user_id>/follow/', FollowUserView.as_view(), name='follow-user'),
    path('users/<int:user_id>/unfollow/', UnfollowUserView.as_view(), name='unfollow-user'),
]
