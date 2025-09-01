

# Eduprompt/urls.py
from django.urls import path
from . import views
from .views import (
    UserPasswordResetView,
    UserPasswordResetDoneView,
    UserPasswordResetConfirmView,
    UserPasswordResetCompleteView,
)

urlpatterns = [
    path('password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Authentication URLs
    path('login/', views.login_view, name='login'),        # name matches LOGIN_URL
    path('register/', views.register_view, name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),

    ]

