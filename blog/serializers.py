from rest_framework import serializers
from .models import BlogPost

class BlogPostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'author_username', 'content', 'excerpt', 
            'image', 'meta_title', 'meta_description', 
            'is_published', 'created_at', 'updated_at'
        ]
