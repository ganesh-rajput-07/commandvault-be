from django.conf import settings
from .models import BlogPost
from vault.sitemaps import BaseSitemap

class BlogSitemap(BaseSitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'https://prompt-deck.vercel.app').strip()
        if frontend_url.endswith('/'):
            frontend_url = frontend_url[:-1]
        return f"{frontend_url}/blog/{obj.slug}"
