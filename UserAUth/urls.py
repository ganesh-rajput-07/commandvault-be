from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, GoogleLoginView, UserProfileView, UserUpdateView, DeactivateAccountView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('user/', UserUpdateView.as_view(), name='user-update'),  # Changed from profile/update/
    path('deactivate/', DeactivateAccountView.as_view(), name='deactivate'),
]
