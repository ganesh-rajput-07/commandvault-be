from django.contrib import admin
from .models import Category, Prompt, PromptVersion, Like, Comment, SavedPrompt, Follow, Notification, Report

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'is_public', 'like_count', 'comment_count', 'created_at']
    list_filter = ['is_public', 'is_deleted', 'created_at']
    search_fields = ['title', 'text', 'owner__username']
    readonly_fields = ['like_count', 'comment_count', 'save_count', 'trend_score', 'times_used']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'prompt', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'user__username', 'prompt__title']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'prompt', 'created_at']
    list_filter = ['created_at']

@admin.register(SavedPrompt)
class SavedPromptAdmin(admin.ModelAdmin):
    list_display = ['user', 'prompt', 'created_at']
    list_filter = ['created_at']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'prompt', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    actions = ['mark_reviewed', 'mark_resolved']

    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')
    mark_reviewed.short_description = "Mark selected as reviewed"

    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved')
    mark_resolved.short_description = "Mark selected as resolved"

admin.site.register(PromptVersion)
