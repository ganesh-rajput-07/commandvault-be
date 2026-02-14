from rest_framework import viewsets, permissions
from .models import BlogPost
from .serializers import BlogPostSerializer

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class BlogPostViewSet(viewsets.ModelViewSet):
    # Default queryset for router initialization
    queryset = BlogPost.objects.filter(is_published=True)
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        # Allow staff to see everything, otherwise only published
        if self.request.user.is_staff:
             return BlogPost.objects.all().order_by('-created_at')
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
