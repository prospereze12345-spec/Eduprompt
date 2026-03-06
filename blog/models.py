from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django_quill.fields import QuillField


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts"
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    featured_image = models.ImageField(upload_to="blog/featured_images/")

    content = QuillField()

    tags = models.ManyToManyField(
        Tag,
        related_name="posts",
        blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:blog_detail", args=[self.slug])

    def __str__(self):
        return self.title






