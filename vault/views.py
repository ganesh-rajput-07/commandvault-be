from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Q, F
from django.db import transaction
from .models import Prompt, Category, Like, SavedPrompt, PromptUnlock
from .serializers import PromptSerializer, CategorySerializer, PromptUnlockSerializer
from .permissions import IsOwnerOrReadOnly
from .utils import auto_tag_and_use_case
from django.core import signing
from django.conf import settings
from django.urls import reverse
import uuid

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
            queryset = queryset.filter(ai_model__icontains=ai_model)
        
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

    def perform_destroy(self, instance):
        """Soft delete the prompt"""
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

    @action(detail=True, methods=['post'])
    def increment_use(self, request, slug=None):
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
        
        return Response({
            'viewed': True,
            'message': 'View already recorded',
            'usage_count': prompt.times_used
        }, status=status.HTTP_200_OK)
    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        prompt = self.get_object()
        user = request.user
        
        if request.method == 'POST':
            with transaction.atomic():
                like, created = Like.objects.get_or_create(user=user, prompt=prompt)
                if created:
                    prompt.like_count = F('like_count') + 1
                    prompt.trend_score = F('trend_score') + 10  # Rewarded more for likes
                    prompt.save(update_fields=['like_count', 'trend_score'])
                    prompt.refresh_from_db()
                    return Response({
                        'liked': True, 
                        'likes_count': prompt.like_count
                    }, status=status.HTTP_201_CREATED)
                return Response({
                    'liked': True, 
                    'likes_count': prompt.like_count
                }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            with transaction.atomic():
                deleted_count, _ = Like.objects.filter(user=user, prompt=prompt).delete()
                if deleted_count > 0:
                    prompt.like_count = F('like_count') - 1
                    prompt.trend_score = F('trend_score') - 10
                    prompt.save(update_fields=['like_count', 'trend_score'])
                    prompt.refresh_from_db()
                return Response({
                    'liked': False, 
                    'likes_count': prompt.like_count
                }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def save_prompt(self, request, slug=None):
        """Action name set to save_prompt to avoid any conflicts with Python/Django reserved words"""
        prompt = self.get_object()
        user = request.user
        
        if request.method == 'POST':
            with transaction.atomic():
                saved, created = SavedPrompt.objects.get_or_create(user=user, prompt=prompt)
                if created:
                    prompt.save_count = F('save_count') + 1
                    prompt.save(update_fields=['save_count'])
                    prompt.refresh_from_db()
                    return Response({
                        'saved': True, 
                        'saves_count': prompt.save_count
                    }, status=status.HTTP_201_CREATED)
                return Response({
                    'saved': True, 
                    'saves_count': prompt.save_count
                }, status=status.HTTP_200_OK)
        
        elif request.method == 'DELETE':
            with transaction.atomic():
                deleted_count, _ = SavedPrompt.objects.filter(user=user, prompt=prompt).delete()
                if deleted_count > 0:
                    prompt.save_count = F('save_count') - 1
                    prompt.save(update_fields=['save_count'])
                    prompt.refresh_from_db()
                return Response({
                    'saved': False, 
                    'saves_count': prompt.save_count
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
    def similar(self, request, slug=None):
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
        ).order_by('-trend_score', '-like_count')
        
        # If this is a fork, ensure parent is first
        results = []
        if prompt.parent_prompt and prompt.parent_prompt.is_public and not prompt.parent_prompt.is_deleted:
            # Check if parent matches criteria (optional, but usually relevant)
            # Actually user wants it ALWAYS first regardless of tags/model match?
            # Yes, "original always first".
            
            # Exclude parent from similar_qs to avoid duplicates
            similar_qs = similar_qs.exclude(id=prompt.parent_prompt.id)
            
            # Add parent to start
            results.append(prompt.parent_prompt)
            
        # Get remaining (limit to 6 total)
        remaining_count = 6 - len(results)
        if remaining_count > 0:
            results.extend(list(similar_qs[:remaining_count]))
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def fork(self, request, slug=None):
        """Fork a prompt to create a new version owned by the current user"""
        source_prompt = self.get_object()
        
        # Prevent forking locked prompts (double check backend side)
        serializer = self.get_serializer(source_prompt)
        # Note: serializer.data access checks permissions/context, but we can do a direct check:
        # If I am not owner and I haven't unlocked it, I shouldn't be valid to fork?
        # Actually, let's just rely on the fact that if they can SEE it, they can fork it?
        # But Requirement says: "Until unlocked: Copy is disabled, Fork button is disabled"
        # So we should enforce lock check here.
        
        is_owner = source_prompt.owner == request.user
        has_unlocked = source_prompt.unlocks.filter(user=request.user).exists()
        
        if not (is_owner or has_unlocked) and source_prompt.owner != request.user:
             return Response(
                 {"detail": "You must unlock this prompt before forking."}, 
                 status=status.HTTP_403_FORBIDDEN
             )
             
        # Check if user has already forked this prompt
        existing_fork = Prompt.objects.filter(
            owner=request.user, 
            parent_prompt=source_prompt
        ).first()
        
        if existing_fork:
            return Response(
                {"detail": "You have already forked this prompt.", "slug": existing_fork.slug}, 
                status=status.HTTP_409_CONFLICT
            )

        with transaction.atomic():
            # Clean up title to avoid "Title (Fork) (Fork)"
            base_title = source_prompt.title
            if base_title.endswith(" (Fork)"):
                new_title = base_title  # Keep same title or maybe append number? simple is keep same.
                # Or if we want to distinguish:
                # new_title = f"{base_title} 2" 
                # For now let's just ensure we don't stack (Fork)
            else:
                new_title = f"{base_title} (Fork)"

            # Create new prompt instance
            new_prompt = Prompt(
                owner=request.user,
                title=new_title,
                text=source_prompt.text,
                ai_model=source_prompt.ai_model,
                tags=source_prompt.tags,
                use_case=source_prompt.use_case,
                category=source_prompt.category,
                example_output=source_prompt.example_output,
                output_type=source_prompt.output_type,
                output_image=source_prompt.output_image,
                output_video=source_prompt.output_video,
                output_audio=source_prompt.output_audio,
                # Fork metadata
                # Fork metadata
                parent_prompt=source_prompt,
                original_creator=source_prompt.original_creator or source_prompt.owner,
                fork_depth=source_prompt.fork_depth + 1,
                # Reset stats
                times_used=0,
                like_count=0,
                comment_count=0,
                save_count=0,
                trend_score=0.0
            )
            new_prompt.save()
            
            # Copy media files if needed (leaving empty for now as simple fork)
            
        return Response(self.get_serializer(new_prompt).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unlock(self, request, slug=None):
        """Unlock a prompt for reading"""
        prompt = self.get_object()
        method = request.data.get('method', 'scroll')
        
        if method not in dict(PromptUnlock.UNLOCK_METHODS):
            return Response({"detail": "Invalid unlock method"}, status=status.HTTP_400_BAD_REQUEST)
            
        unlock, created = PromptUnlock.objects.get_or_create(
            user=request.user, 
            prompt=prompt,
            defaults={'unlock_method': method}
        )
        
        return Response({'unlocked': True}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def share_token(self, request, slug=None):
        """Generate a secure share token/URL for QR codes"""
        prompt = self.get_object()
        
        # Only owner should generate generic share tokens? Or anyone?
        # Let's allow anyone to share.
        
        signer = signing.TimestampSigner()
        value = signing.dumps({'prompt_id': prompt.id, 'source': 'qr'})
        token = signer.sign(value)
        
        # Construct URL (assuming frontend route)
        # Using settings.FRONTEND_URL ideally
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        share_url = f"{frontend_url}/prompt/{prompt.slug}?token={token}&source=qr"
        
        return Response({
            'share_url': share_url,
            'token': token
        })

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
