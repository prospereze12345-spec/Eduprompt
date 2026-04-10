from django.urls import path
from . import views

urlpatterns = [
    path("tool/submit/", views.grammar_tool_redirect, name="grammar_tool_redirect"),
    path("<slug:slug>/", views.seo_page, name="seo_page"),
]