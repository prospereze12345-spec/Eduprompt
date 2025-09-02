from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Tag
from django.core.paginator import Paginator
from django.conf import settings
from .models import BlogPost, Tag
import math


def blog_list(request):
    # Get all posts, newest first
    posts = BlogPost.objects.all().order_by('-created_at')
    
    # Pagination: 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Sidebar: latest 5 posts for "Older Posts" widget
    latest_posts = BlogPost.objects.all().order_by('-created_at')[:5]
    
    # Sidebar: all tags
    tags = Tag.objects.all()

    context = {
        'page_obj': page_obj,
        'latest_posts': latest_posts,
        'tags': tags,
        'AFRICAN_LANGUAGES': getattr(settings, 'AFRICAN_LANGUAGES', []),
    }
    
    return render(request, 'blog/blog_list.html', context)






def blog_detail(request, slug):
    """
    Display a single blog post with author info and comments.
    Sidebar, tags, and latest posts have been removed.
    """
    post = get_object_or_404(BlogPost, slug=slug)


    word_count = len(post.content.html.split())
    read_time = math.ceil(word_count / 200) 

    context = {
        'post': post,
        'AFRICAN_LANGUAGES': getattr(settings, 'AFRICAN_LANGUAGES', []),
    }

    return render(request, "blog/blog_detail.html", context)



from django.shortcuts import render
from .models import BlogPost  # adjust if your model name is different

def recent_posts_view(request):
    blog_list = BlogPost.objects.all().order_by('-created_at')[:3]  # latest 6 posts
    return render(request, 'your_template.html', {
        'blog_list': blog_list
    })

