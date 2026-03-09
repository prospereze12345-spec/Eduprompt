from django.urls import path
from . import views
from .views import health_check  # import the view


urlpatterns = [
    
    # AJAX endpoints
    path("ajax/signup/", views.ajax_signup, name="ajax_signup"),
    path("send-magic-link/", views.send_magic_link, name="send_magic_link"),
    path("magic-login/<str:token>/", views.magic_login, name="magic_login"),
    path('health/', health_check, name='health_check'),

]
