# urls.py
from django.urls import path
from .views import quiz_generator, generate_quiz, download_quiz_pdf

urlpatterns = [
    path("quiz/", quiz_generator, name="quiz_generator"),
    path("quiz/generate/", generate_quiz, name="generate_quiz"),
    path("quiz/download/", download_quiz_pdf, name="download_quiz_pdf"),
]
