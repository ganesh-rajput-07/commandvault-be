from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from .models import Like, Comment, SavedPrompt, Follow, Notification, Report
from .serializers import (LikeSerializer, CommentSerializer, SavedPromptSerializer, 
                          FollowSerializer, NotificationSerializer, ReportSerializer)

class LikeViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        prompt_id = request.data.get('prompt_id')
        if not prompt_id:
            return Response({'error': 'prompt_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        like, created = Like.objects.get_or_create(user=request.user, prompt_id=prompt_id)
        
        if not created:
            like.delete()
            Like.objects.filter(prompt_id=prompt_id).update(like_count=F('like_count') - 1)
            return Response({'liked': False, 'message': 'Unliked'}, status=status.HTTP_200_OK)
        else:
            from .models import Prompt
            Prompt.objects.filter(id=prompt_id).update(like_count=F('like_count') + 1)
            return Response({'liked': True, 'message': 'Liked'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_likes(self, request):
        likes = Like.objects.filter(user=request.user).select_related('prompt')
        page = self.paginate_queryset(likes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(likes, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        prompt_id = self.request.query_params.get('prompt_id')
        if prompt_id:
            return Comment.objects.filter(prompt_id=prompt_id).select_related('user')
        return Comment.objects.filter(user=self.request.user).select_related('prompt')

    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        from .models import Prompt
        Prompt.objects.filter(id=comment.prompt_id).update(comment_count=F('comment_count') + 1)

    def perform_destroy(self, instance):
        prompt_id = instance.prompt_id
        instance.delete()
        from .models import Prompt
        Prompt.objects.filter(id=prompt_id).update(comment_count=F('comment_count') - 1)

class SavedPromptViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedPromptSerializer

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        prompt_id = request.data.get('prompt_id')
        if not prompt_id:
            return Response({'error': 'prompt_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        saved, created = SavedPrompt.objects.get_or_create(user=request.user, prompt_id=prompt_id)
        
        if not created:
            saved.delete()
            from .models import Prompt
            Prompt.objects.filter(id=prompt_id).update(save_count=F('save_count') - 1)
            return Response({'saved': False, 'message': 'Unsaved'}, status=status.HTTP_200_OK)
        else:
            from .models import Prompt
            Prompt.objects.filter(id=prompt_id).update(save_count=F('save_count') + 1)
            return Response({'saved': True, 'message': 'Saved'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_saved(self, request):
        saved = SavedPrompt.objects.filter(user=request.user).select_related('prompt')
        page = self.paginate_queryset(saved)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(saved, many=True)
        return Response(serializer.data)

class FollowViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowSerializer

    @action(detail=False, methods=['post'])
    def toggle(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if str(user_id) == str(request.user.id):
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(follower=request.user, following_id=user_id)
        
        if not created:
            follow.delete()
            from django.contrib.auth import get_user_model
            User = get_user_model()
            User.objects.filter(id=user_id).update(follower_count=F('follower_count') - 1)
            User.objects.filter(id=request.user.id).update(following_count=F('following_count') - 1)
            return Response({'following': False, 'message': 'Unfollowed'}, status=status.HTTP_200_OK)
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            User.objects.filter(id=user_id).update(follower_count=F('follower_count') + 1)
            User.objects.filter(id=request.user.id).update(following_count=F('following_count') + 1)
            return Response({'following': True, 'message': 'Followed'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        user_id = request.query_params.get('user_id', request.user.id)
        follows = Follow.objects.filter(following_id=user_id).select_related('follower')
        page = self.paginate_queryset(follows)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(follows, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def following(self, request):
        user_id = request.query_params.get('user_id', request.user.id)
        follows = Follow.objects.filter(follower_id=user_id).select_related('following')
        page = self.paginate_queryset(follows)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(follows, many=True)
        return Response(serializer.data)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related('related_user', 'related_prompt')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All marked as read'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)

class ReportViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReportSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Report.objects.all().select_related('reporter', 'prompt')
        return Report.objects.filter(reporter=self.request.user).select_related('prompt')

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
