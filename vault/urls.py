from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PromptViewSet, CategoryViewSet
from .social_views import (LikeViewSet, CommentViewSet, SavedPromptViewSet, 
                            FollowViewSet, NotificationViewSet, ReportViewSet)
from .analytics_views import AnalyticsView, PopularTagsView

router = DefaultRouter()
router.register(r'prompts', PromptViewSet, basename='prompt')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'saved', SavedPromptViewSet, basename='saved')
router.register(r'follows', FollowViewSet, basename='follow')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = router.urls + [
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('tags/popular/', PopularTagsView.as_view(), name='popular-tags'),
]
