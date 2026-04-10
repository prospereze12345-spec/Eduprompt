from django.shortcuts import render, redirect
from .data import PAGES


def seo_page(request, slug):
    page = PAGES.get(slug)

    if not page:
        return render(request, "404.html")

    return render(request, "seo_pages/page.html", {"page": page})


def grammar_tool_redirect(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        request.session["tool_text"] = text
        return redirect("/grammar-checker/")
    
    return redirect("/")