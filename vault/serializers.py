from rest_framework import serializers
from .models import Prompt, Category, PromptVersion, Like, Comment, SavedPrompt, PromptView, Follow, Notification, Report
from django.contrib.auth import get_user_model

User = get_user_model()

class PromptVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptVersion
        fields = ['id', 'old_title', 'old_text', 'created_at']

class OwnerSerializer(serializers.ModelSerializer):
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar', 'follower_count', 'is_following']
    
    def get_is_following(self, obj):
        """Check if the current user is following this user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False


class PromptSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    versions = PromptVersionSerializer(many=True, read_only=True)
    
    # Computed fields for current user's interaction state
    is_liked_by_user = serializers.SerializerMethodField()
    is_saved_by_user = serializers.SerializerMethodField()
    is_viewed_by_user = serializers.SerializerMethodField()
    
    # Field aliases for frontend compatibility
    likes_count = serializers.IntegerField(source='like_count', read_only=True)
    saves_count = serializers.IntegerField(source='save_count', read_only=True)
    usage_count = serializers.IntegerField(source='times_used', read_only=True)

    class Meta:
        model = Prompt
        fields = ['id', 'owner', 'title', 'slug', 'text', 'ai_model', 'example_output', 
                  'output_image', 'output_video', 'output_audio', 'output_type',
                  'tags', 'use_case', 'category', 'is_public',
                  'usage_count', 'likes_count', 'comment_count', 'saves_count', 'trend_score',
                  'is_liked_by_user', 'is_saved_by_user', 'is_viewed_by_user',
                  'created_at', 'updated_at', 'versions']
        read_only_fields = ['owner', 'slug', 'usage_count', 'likes_count', 'comment_count', 
                            'saves_count', 'trend_score', 'created_at', 'updated_at']
    
    def get_is_liked_by_user(self, obj):
        """Check if the current user has liked this prompt"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_is_saved_by_user(self, obj):
        """Check if the current user has saved this prompt"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved_by.filter(user=request.user).exists()
        return False
    
    def get_is_viewed_by_user(self, obj):
        """Check if the current user has viewed this prompt"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.viewed_by.filter(user=request.user).exists()
        return False

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class LikeSerializer(serializers.ModelSerializer):
    user = OwnerSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'prompt', 'created_at']
        read_only_fields = ['user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = OwnerSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'prompt', 'text', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class SavedPromptSerializer(serializers.ModelSerializer):
    prompt = PromptSerializer(read_only=True)
    
    class Meta:
        model = SavedPrompt
        fields = ['id', 'prompt', 'created_at']
        read_only_fields = ['created_at']

class FollowSerializer(serializers.ModelSerializer):
    follower = OwnerSerializer(read_only=True)
    following = OwnerSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'following', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    related_user = OwnerSerializer(read_only=True)
    related_prompt_title = serializers.SerializerMethodField()
    related_prompt_slug = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'content', 'is_read', 'related_prompt', 
                  'related_user', 'created_at', 'related_prompt_title', 'related_prompt_slug', 'time_ago']
        read_only_fields = ['notification_type', 'content', 'related_prompt', 
                            'related_user', 'created_at']
    
    def get_related_prompt_title(self, obj):
        return obj.related_prompt.title if obj.related_prompt else None
    
    def get_related_prompt_slug(self, obj):
        return obj.related_prompt.slug if obj.related_prompt else None
    
    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d ago"
        else:
            return obj.created_at.strftime("%b %d")


class ReportSerializer(serializers.ModelSerializer):
    reporter = OwnerSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'reporter', 'prompt', 'reason', 'status', 'created_at', 'updated_at']
        read_only_fields = ['reporter', 'status', 'created_at', 'updated_at']
