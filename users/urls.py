from django.urls import path
from . import views

urlpatterns = [
    # AJAX endpoints
    path("ajax/signup/", views.ajax_signup, name="ajax_signup"),
    path('ajax/login/', views.ajax_login, name='ajax_login'),
    path('ajax/send-magic-link/', views.send_magic_link, name='send_magic_link'),

    # Magic login URL (clicked from email)
    path('magic-login/', views.magic_login, name='magic_login'),
    path("send-magic-link/", views.send_magic_link, name="send_magic_link"),

]
