from django.contrib import admin
from django.utils.html import format_html
from .models import BlogPost, Tag


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'image_tag')
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('status', 'created_at')
    search_fields = ('title',)

    def image_tag(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="height:50px"/>', obj.featured_image.url)
        return "No Image"
    image_tag.short_description = 'Featured Image'


admin.site.register(Tag)