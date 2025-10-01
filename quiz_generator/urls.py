# urls.py
from django.urls import path
from .import views
urlpatterns = [
        path("quiz/", views.quiz_generator, name="quiz_generator"),
        path("quiz/generate/", views.generate_quiz, name="generate_quiz"),
        path("quiz/download/", views.download_quiz_pdf, name="download_quiz_pdf"),
        path('quiz/subscription/status/', views.quiz_status, name='quiz_status'),
        path("quiz-subscription-status/", views.quiz_subscription_status, name="quiz_subscription_status"),
        path("quiz-start-subscription/", views.quiz_start_subscription, name="quiz_start_subscription"),
        path("quiz-verify-subscription/", views.quiz_verify_subscription, name="quiz_verify_subscription"),
        path("upload-quiz/", views.upload_and_generate_quiz, name="upload_and_generate_quiz"),

]
