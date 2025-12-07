from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import Prompt
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class AnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_prompts = Prompt.objects.filter(is_deleted=False).count()
        public_prompts = Prompt.objects.filter(is_public=True, is_deleted=False).count()
        private_prompts = Prompt.objects.filter(is_public=False, is_deleted=False).count()
        
        most_copied = Prompt.objects.filter(is_deleted=False).order_by('-times_used')[:10].values(
            'id', 'title', 'times_used', 'owner__username'
        )
        
        most_liked = Prompt.objects.filter(is_deleted=False).order_by('-like_count')[:10].values(
            'id', 'title', 'like_count', 'owner__username'
        )
        
        recent_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'total_prompts': total_prompts,
            'public_prompts': public_prompts,
            'private_prompts': private_prompts,
            'public_private_ratio': f"{public_prompts}:{private_prompts}",
            'most_copied_prompts': list(most_copied),
            'most_liked_prompts': list(most_liked),
            'new_users_last_30_days': recent_users
        })

class PopularTagsView(APIView):
    def get(self, request):
        from django.db.models import JSONField
        from collections import Counter
        
        prompts = Prompt.objects.filter(is_public=True, is_deleted=False).values_list('tags', flat=True)
        all_tags = []
        for tags in prompts:
            if tags:
                all_tags.extend(tags)
        
        tag_counts = Counter(all_tags)
        popular_tags = [{'tag': tag, 'count': count} for tag, count in tag_counts.most_common(20)]
        
        return Response({'popular_tags': popular_tags})
