from django.db import models
from django.conf import settings  # <-- use this for custom user
from django.utils.text import slugify
from django_quill.fields import QuillField  # Quill editor field


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    # Use settings.AUTH_USER_MODEL instead of direct User import
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    featured_image = models.ImageField(upload_to="blog/featured_images/")
    content = QuillField()  # Rich text: headings, paragraphs, inline images
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title




