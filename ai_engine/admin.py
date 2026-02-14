from django.contrib import admin
from .models import AIProvider, AIModel

@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'is_active', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'api_id', 'is_active')
    search_fields = ('name', 'api_id')
    list_filter = ('provider', 'is_active')
