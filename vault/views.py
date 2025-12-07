from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Q, F
from .models import Prompt, Category
from .serializers import PromptSerializer, CategorySerializer
from .permissions import IsOwnerOrReadOnly
from .utils import auto_tag_and_use_case

class PromptViewSet(viewsets.ModelViewSet):
    serializer_class = PromptSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Prompt.objects.filter(is_deleted=False)
        if self.request.user.is_authenticated:
            queryset = queryset.filter(Q(is_public=True) | Q(owner=self.request.user))
        else:
            queryset = queryset.filter(is_public=True)
        
        # Prefetch likes and saves to avoid N+1 queries
        return queryset.select_related('owner', 'category').prefetch_related(
            'likes', 'saved_by'
        ).order_by('-updated_at')

    def perform_create(self, serializer):
        tags, use_case = auto_tag_and_use_case(
            serializer.validated_data.get('text', '') + ' ' + 
            serializer.validated_data.get('title', '')
        )
        existing_tags = serializer.validated_data.get('tags') or []
        
        # Ensure existing_tags is a list
        if isinstance(existing_tags, str):
            existing_tags = [existing_tags]
        
        # Merge tags
        merged = list(dict.fromkeys(existing_tags + tags))
        serializer.save(owner=self.request.user, tags=merged, use_case=use_case)

    @action(detail=True, methods=['post'])
    def increment_use(self, request, pk=None):
        prompt = self.get_object()
        prompt.times_used = F('times_used') + 1
        prompt.save()
        prompt.refresh_from_db()
        return Response({'times_used': prompt.times_used})

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q', '')
        tags = request.query_params.getlist('tags')
        qs = self.get_queryset()
        
        if tags:
            qs = qs.filter(tags__contains=tags)
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(text__icontains=q) | Q(tags__contains=[q])
            )
        
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def mine(self, request):
        qs = Prompt.objects.filter(owner=request.user, is_deleted=False).prefetch_related(
            'likes', 'saved_by'
        ).order_by('-created_at')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        qs = Prompt.objects.filter(is_public=True, is_deleted=False).prefetch_related(
            'likes', 'saved_by'
        ).order_by('-trend_score', '-like_count')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
