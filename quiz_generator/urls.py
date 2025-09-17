# urls.py
from django.urls import path
from .import views
urlpatterns = [
        path("quiz/", views.quiz_generator, name="quiz_generator"),
        path("quiz/generate/", views.generate_quiz, name="generate_quiz"),
        path("quiz/download/", views.download_quiz_pdf, name="download_quiz_pdf"),

]
