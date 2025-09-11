from django.urls import path
from . import views

urlpatterns = [
    path('', views.essay_page, name='essay_page'),

    path("essay-generate/", views.essay_generate, name="essay_generate"),

    path('essay/download/', views.download_essay_pdf, name='download_essay_pdf'),
    path("translate/", views.translate_text, name="translate_text"),  
]
