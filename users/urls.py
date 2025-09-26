from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('ajax/signup/', views.ajax_signup, name='ajax_signup'),
    path('ajax/login/', views.ajax_login, name='ajax_login'),
    
    path("password_reset/",
         auth_views.PasswordResetView.as_view(
             template_name="password_reset.html"  # your custom template
         ),
         name="password_reset"),

    path("password_reset/done/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="password_reset_done.html"
         ),
         name="password_reset_done"),

    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="password_reset_confirm.html"
         ),
         name="password_reset_confirm"),
 path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html",
            extra_context={"use_modal_login": True},  # optional
        ),
        name="password_reset_complete",
    ),
]


