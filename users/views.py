# users/views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from threading import Timer
from .utils import send_welcome_email

@require_POST
def ajax_signup(request):
    email = request.POST.get('email')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')

    if not all([email, password1, password2]):
        return JsonResponse({'user_authenticated': False, 'errors': 'All fields are required.'})

    if password1 != password2:
        return JsonResponse({'user_authenticated': False, 'errors': 'Passwords do not match.'})

    if User.objects.filter(email=email).exists():
        return JsonResponse({'user_authenticated': False, 'errors': 'Email already registered.'})

    user = User.objects.create_user(username=email, email=email, password=password1)
    login(request, user)

    # Send welcome email after 3 seconds
    Timer(3.0, send_welcome_email, args=[user]).start()

    return JsonResponse({'user_authenticated': True})

@require_POST
def ajax_login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({'user_authenticated': True})
    return JsonResponse({'user_authenticated': False, 'errors': 'Invalid credentials.'})

