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
        return redirect('index')  # prevent logged-in users from seeing register

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login user
            messages.success(request, "Account created successfully. Welcome!")
            return redirect('index')  # 👈 make sure 'index' exists in urls.py
        else:
            # Form not valid, show errors
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
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
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



@login_required
def dashboard_view(request):
    user = request.user
    profile = getattr(user, 'profile', None) 

    country_code = getattr(profile, 'country', 'NG').upper() if profile else 'NG'
    wallet_balance_usd = getattr(profile, 'wallet_balance', 0.0) if profile else 0.0
    subscription_plan = getattr(profile, 'subscription_plan', 'Free') if profile else 'Free'
    subscription_expiry = getattr(profile, 'subscription_expiry', 'N/A') if profile else 'N/A'

    currency_code = settings.DEFAULT_CURRENCY
    currency_symbol = get_currency_symbol(currency_code)
    local_balance = round(wallet_balance_usd, 2)

    try:
        url = f"{settings.EXCHANGE_API_URL}/{settings.EXCHANGE_API_KEY}/latest/USD"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        conversion_rates = data.get("conversion_rates", {})

        if country_code in conversion_rates:
            currency_code = country_code
        else:
            currency_code = settings.DEFAULT_CURRENCY

        currency_symbol = get_currency_symbol(currency_code)
        rate = conversion_rates.get(currency_code, 1)
        local_balance = round(wallet_balance_usd * rate, 2)

    except Exception as e:
        print("Currency API error:", e)
        currency_code = settings.DEFAULT_CURRENCY
        currency_symbol = get_currency_symbol(currency_code)
        local_balance = round(wallet_balance_usd, 2)

    context = {
        "user": user,
        "wallet_balance": f"{currency_symbol}{local_balance}",
        "subscription_plan": subscription_plan,
        "subscription_expiry": subscription_expiry,
    }

    return render(request, "dashboard.html", context)





def get_user_currency(request):
    currency_symbol = "₦"  # default NGN

    try:
        
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '') or request.META.get('REMOTE_ADDR', '')

        if ip_address:
            response = requests.get(f"https://ipapi.co/{ip_address}/json/")
            response.raise_for_status()
            data = response.json()
            country_code = data.get("country_code", "NG")  

            currency_symbol = get_currency_symbol(country_code)

    except Exception as e:
        print("Currency detection error:", e)

    return JsonResponse({'currency_symbol': currency_symbol})

