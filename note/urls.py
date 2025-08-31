from django.urls import path
from . import views

urlpatterns = [
    path("", views.note_page, name="note_page"),
    path("download_pdf/", views.download_note_pdf, name="download_note_pdf"),
    path("generate/", views.generate_note, name="generate_note"),  # <--- just "generate/"
]

