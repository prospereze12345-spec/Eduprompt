from django.contrib.sitemaps import Sitemap
from .models import SeoPage


class SeoPageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return SeoPage.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return f"/{obj.slug}/"