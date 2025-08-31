from django.urls import path
from . import views

urlpatterns = [
    path('letter-writer/', views.letter_writer, name='letter_writer'),
    path('download-letter/', views.download_letter_pdf, name='download_letter_pdf'),
    path("generate-letter/", views.generate_letter, name="generate_letter"),

]
