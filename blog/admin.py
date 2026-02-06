from django.contrib import admin
from .models import BlogPost, Tag

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "content")
    list_filter = ("created_at", "tags")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)

