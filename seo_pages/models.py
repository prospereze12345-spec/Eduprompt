from django.db import models
from django.db import models

class SeoPage(models.Model):
    group = models.CharField(max_length=100)  # rewriting, grammar, etc
    keyword = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)

    title = models.CharField(max_length=255)
    meta_description = models.TextField()

    h1 = models.CharField(max_length=255)
    intro = models.TextField()

    problem = models.TextField()
    solution = models.TextField()

    benefits = models.JSONField(default=list)  # your array
    use_case = models.TextField()

    faq = models.JSONField(default=list)  # list of Q/A objects

    cta = models.TextField()

    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
