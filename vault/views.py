from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from .models import Prompt, Category
from .serializers import PromptSerializer, CategorySerializer
from .utils import auto_tag_and_use_case

class PromptViewSet(viewsets.ModelViewSet):
    queryset = Prompt.objects.all().order_by('-updated_at')
    serializer_class = PromptSerializer

    def perform_create(self, serializer):
        tags, use_case = auto_tag_and_use_case(serializer.validated_data.get('text', '') + ' ' + serializer.validated_data.get('title', ''))
        # merge tags
        existing_tags = serializer.validated_data.get('tags') or []
        merged = list(dict.fromkeys(existing_tags + tags))
        serializer.save(tags=merged, use_case=use_case)

    @action(detail=True, methods=['post'])
    def increment_use(self, request, pk=None):
        prompt = self.get_object()
        prompt.times_used = models.F('times_used') + 1
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
            query = SearchQuery(q)
            vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
            qs = qs.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.1).order_by('-rank')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
