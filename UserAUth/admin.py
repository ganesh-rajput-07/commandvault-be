from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'is_google_account', 'is_active', 'follower_count', 'following_count', 'date_joined']
    list_filter = ['is_google_account', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username']
    readonly_fields = ['follower_count', 'following_count', 'date_joined', 'profile_updated_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'avatar_url', 'google_id', 'is_google_account', 
                                        'follower_count', 'following_count', 'profile_updated_at')}),
    )
