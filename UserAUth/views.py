from rest_framework import generics, status, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserProfileSerializer, UserUpdateSerializer
from .google_auth import verify_google_token, get_or_create_google_user

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)

        idinfo = verify_google_token(token)
        if not idinfo:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)

        email = idinfo.get('email')
        existing_user = User.objects.filter(email=email).first()
        
        if existing_user and not existing_user.is_google_account:
            existing_user.google_id = idinfo.get('sub')
            existing_user.is_google_account = True
            existing_user.save()
            user = existing_user
        else:
            user = get_or_create_google_user(idinfo)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        })

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserUpdateSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class PublicUserProfileView(generics.RetrieveAPIView):
    """View for getting any user's public profile by username"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    lookup_field = 'username'
    
    def get_queryset(self):
        return User.objects.filter(is_active=True)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class DeactivateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.soft_delete()
        return Response({'message': 'Account deactivated successfully'}, status=status.HTTP_200_OK)

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        from vault.models import Follow, Notification
        
        if request.user.id == user_id:
            return Response({'error': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if created:
            # Update follower count
            user_to_follow.follower_count += 1
            user_to_follow.save()
            
            # Create notification
            Notification.objects.create(
                user=user_to_follow,
                notification_type='follow',
                content=f'{request.user.username} started following you',
                related_user=request.user
            )
            
            return Response({'message': 'Successfully followed user'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Already following this user'}, status=status.HTTP_200_OK)

class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        from vault.models import Follow
        
        try:
            user_to_unfollow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        deleted_count, _ = Follow.objects.filter(
            follower=request.user,
            following=user_to_unfollow
        ).delete()
        
        if deleted_count > 0:
            # Update follower count
            user_to_unfollow.follower_count = max(0, user_to_unfollow.follower_count - 1)
            user_to_unfollow.save()
            return Response({'message': 'Successfully unfollowed user'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not following this user'}, status=status.HTTP_400_BAD_REQUEST)
