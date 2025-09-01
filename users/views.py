# Eduprompt/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from .models import Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import requests





def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # Prevent logged-in users from seeing register page

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Save the user only
            user = form.save()

            # Log the user in immediately
            login(request, user)
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('index')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()

    context = {
        'form': form,
        'AFRICAN_LANGUAGES': getattr(settings, 'AFRICAN_LANGUAGES', []),
    }
    return render(request, 'register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # Prevent logged-in users from seeing login page

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    context = {
        'form': form,
        'AFRICAN_LANGUAGES': getattr(settings, 'AFRICAN_LANGUAGES', []),
    }
    return render(request, 'login.html', context)





def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')



class UserPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'



CURRENCY_SYMBOLS = {
    "NGN": "₦", "GHS": "₵", "KES": "KSh", "UGX": "USh", "TZS": "TSh",
    "MWK": "MK", "LSL": "L", "BIF": "FBu", "DJF": "Fdj", "GNF": "FG",
    "KMF": "CF", "MGA": "Ar", "RWF": "FRw", "ZAR": "R", "USD": "$",
    "EUR": "€", "GBP": "£", "AUD": "$", "CAD": "$", "JPY": "¥",
    "INR": "₹", "CNY": "¥", "MXN": "$", "BRL": "R$", "CHF": "CHF",
    "SEK": "kr", "NOK": "kr", "DKK": "kr", "PLN": "zł", "TRY": "₺",
    "RUB": "₽", "KRW": "₩", "MYR": "RM", "THB": "฿", "PHP": "₱",
    "IDR": "Rp", "AED": "د.إ", "SAR": "ر.س", "EGP": "ج.م", "ILS": "₪",
    "COP": "$", "ARS": "$", "CLP": "$", "PEN": "S/"
}


def get_currency_symbol(currency_code):
    return CURRENCY_SYMBOLS.get(currency_code, "₦")








