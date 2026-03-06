from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost   # change to your blog model name


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            'index',
            'blog:blog',   # blog list page
            'about',
            'privacy_policy',
            'Terms_and_Condition',
            'contact',
            'website',
        ]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog:blog_detail', args=[obj.slug])