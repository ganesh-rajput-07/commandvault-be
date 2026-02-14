from django.contrib.sitemaps import Sitemap
from django.conf import settings
from .models import Prompt
from UserAUth.models import User

class BaseSitemap(Sitemap):
    protocol = None
    
    def get_urls(self, page=1, site=None, protocol=None):
        urls = super().get_urls(page, site, protocol)
        for url in urls:
            loc = url['location']
            # Fix double domain issue if Django prepends backend domain to frontend URL
            if 'https://prompt-deck.vercel.app' in loc:
                index = loc.find('https://prompt-deck.vercel.app')
                if index > 0:
                    url['location'] = loc[index:]
        return urls

class PromptSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Prompt.objects.filter(is_public=True, is_deleted=False)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # Point to the React Frontend URL. Strip whitespace.
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://prompt-deck.vercel.app').strip()
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        return f"{frontend_url}/prompt/{obj.slug}"

class UserSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return User.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.profile_updated_at

    def location(self, obj):
        # Point to the React Frontend URL. Strip whitespace.
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://prompt-deck.vercel.app').strip()
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        return f"{frontend_url}/user/{obj.username}"

class StaticSitemap(BaseSitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['/', '/explore', '/trending', '/login', '/register']

    def location(self, item):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://prompt-deck.vercel.app').strip()
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        return f"{frontend_url}{item}"
