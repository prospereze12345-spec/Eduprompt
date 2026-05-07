# Eduprompt/urls.py
from django.urls import path
from . import views
from .views import improve_text
from django.urls import path
from . import views
from .views import improve_text

urlpatterns = [
    path('grammar-upload/', views.grammar_upload_view, name='grammar-upload'),
    path("improve-text/", improve_text, name="improve_text"),

    path("grammar-checker/", views.grammar_checker, name="grammar_checker"),

    path("grammar/subscription/status/", views.grammar_status, name="grammar_status"),
    path("grammar-subscription-status/", views.grammar_subscription_status, name="grammar_subscription_status"),
    path("grammar-start-subscription/", views.grammar_start_subscription, name="grammar_start_subscription"),
    path("grammar-verify-subscription/", views.grammar_verify_subscription, name="grammar_verify_subscription"),

]
