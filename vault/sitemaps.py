from django.contrib.sitemaps import Sitemap
from django.conf import settings
from .models import Prompt
from UserAUth.models import User

class PromptSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = None  # Explicitly disable protocol to prevent double-domain prepending

    def items(self):
        return Prompt.objects.filter(is_public=True, is_deleted=False)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # Point to the React Frontend URL. Strip whitespace.
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://prompt-deck.vercel.app').strip()
        # Remove trailing slash if present to avoid double slashes
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        return f"{frontend_url}/prompt/{obj.slug}"

class UserSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = None

    def items(self):
        return User.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.profile_updated_at

    def location(self, obj):
        # Point to the React Frontend URL. Strip whitespace.
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://prompt-deck.vercel.app').strip()
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        # Route is /user/:username based on App.js
        return f"{frontend_url}/user/{obj.username}"

class StaticSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    protocol = None

    def items(self):
        return ['/', '/explore', '/trending', '/login', '/register']

    def location(self, item):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://prompt-deck.vercel.app').strip()
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        return f"{frontend_url}{item}"
