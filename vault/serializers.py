from rest_framework import serializers
from .models import Prompt, Category, PromptVersion

class PromptVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptVersion
        fields = ['id', 'old_title', 'old_text', 'created_at']

class PromptSerializer(serializers.ModelSerializer):
    versions = PromptVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Prompt
        fields = ['id', 'title', 'text', 'tags', 'use_case', 'category', 'times_used', 'created_at', 'updated_at', 'versions']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
