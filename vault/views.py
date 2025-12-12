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
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Prompt.objects.filter(is_deleted=False)
        if self.request.user.is_authenticated:
            queryset = queryset.filter(Q(is_public=True) | Q(owner=self.request.user))
        else:
            queryset = queryset.filter(is_public=True)
        
        # Filter by owner (for user profile pages)
        owner_id = self.request.query_params.get('owner_id', '').strip()
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
        
        # Search functionality via query parameters
        search_query = self.request.query_params.get('search', '').strip()
        ai_model = self.request.query_params.get('ai_model', '').strip()
        
        if search_query:
            # Search across multiple fields: title, content, tags, username, AI model
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(text__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(ai_model__icontains=search_query) |
                Q(owner__username__icontains=search_query)
            )
        
        if ai_model and ai_model.lower() != 'all':
            queryset = queryset.filter(ai_model__iexact=ai_model)
        
        # Prefetch likes, saves, and views to avoid N+1 queries
        return queryset.select_related('owner', 'category').prefetch_related(
            'likes', 'saved_by', 'viewed_by'
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def record_view(self, request, slug=None):
        """Record that user viewed this prompt (opened detail modal)"""
        from .models import PromptView
        prompt = self.get_object()
        
        view, created = PromptView.objects.get_or_create(user=request.user, prompt=prompt)
        
        if created:
            # Increment view count only on first view
            prompt.times_used = F('times_used') + 1
            prompt.trend_score = F('trend_score') + 1
            prompt.save(update_fields=['times_used', 'trend_score'])
            prompt.refresh_from_db()
            return Response({
                'viewed': True,
                'message': 'View recorded',
                'usage_count': prompt.times_used
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'viewed': True,
                'message': 'Already viewed',
                'usage_count': prompt.times_used
            }, status=status.HTTP_200_OK)

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
            'likes', 'saved_by', 'viewed_by'
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
            'likes', 'saved_by', 'viewed_by'
        ).order_by('-trend_score', '-like_count')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Get similar prompts based on AI model and tags"""
        prompt = self.get_object()
        
        # Find prompts with same AI model or overlapping tags
        similar_qs = Prompt.objects.filter(
            is_public=True,
            is_deleted=False
        ).exclude(id=prompt.id)
        
        # Filter by same AI model or overlapping tags
        if prompt.ai_model:
            similar_qs = similar_qs.filter(
                Q(ai_model=prompt.ai_model) | Q(tags__overlap=prompt.tags or [])
            )
        elif prompt.tags:
            similar_qs = similar_qs.filter(tags__overlap=prompt.tags)
        
        # Order by relevance (same model first, then by trend score)
        similar_qs = similar_qs.select_related('owner').prefetch_related(
            'likes', 'saved_by', 'viewed_by'
        ).order_by('-trend_score', '-like_count')[:6]
        
        serializer = self.get_serializer(similar_qs, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
