from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"      
    priority = 0.8             

    def items(self):
        return [
            'index',
            'quiz_generator',
            'essay_page',
            'grammar_checker',
            'about',
            'privacy_policy',
            'Terms_and_Condition',
            'contact',
            'website',
        ]

    def location(self, item):
        return reverse(item)
