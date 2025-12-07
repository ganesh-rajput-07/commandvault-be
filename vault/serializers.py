from rest_framework import serializers
from .models import Prompt, Category, PromptVersion, Like, Comment, SavedPrompt, Follow, Notification, Report
from django.contrib.auth import get_user_model

User = get_user_model()

class PromptVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptVersion
        fields = ['id', 'old_title', 'old_text', 'created_at']

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar_url']

class PromptSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    versions = PromptVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Prompt
        fields = ['id', 'owner', 'title', 'text', 'ai_model', 'example_output', 'tags', 'use_case', 'category', 'is_public',
                  'times_used', 'like_count', 'comment_count', 'save_count', 'trend_score',
                  'created_at', 'updated_at', 'versions']
        read_only_fields = ['owner', 'times_used', 'like_count', 'comment_count', 
                            'save_count', 'trend_score', 'created_at', 'updated_at']

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
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'content', 'is_read', 'related_prompt', 
                  'related_user', 'created_at']
        read_only_fields = ['notification_type', 'content', 'related_prompt', 
                            'related_user', 'created_at']

class ReportSerializer(serializers.ModelSerializer):
    reporter = OwnerSerializer(read_only=True)
    
    class Meta:
        model = Report
        fields = ['id', 'reporter', 'prompt', 'reason', 'status', 'created_at', 'updated_at']
        read_only_fields = ['reporter', 'status', 'created_at', 'updated_at']
