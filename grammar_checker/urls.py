from django.urls import path
from . import views

urlpatterns = [
    # Grammar checker page
    path('grammar-checker/', views.grammar_checker, name='grammar_checker'),
    path('grammar-upload/', views.grammar_upload_view, name='grammar-upload'),

 # # Grammar subscription routes
path("grammar/subscription/status/", views.grammar_status, name="grammar_status"),
path("grammar-subscription-status/", views.grammar_subscription_status, name="grammar_subscription_status"),
path("grammar-start-subscription/", views.grammar_start_subscription, name="grammar_start_subscription"),
path("grammar-verify-subscription/", views.grammar_verify_subscription, name="grammar_verify_subscription"),

]
