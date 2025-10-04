# users/views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from threading import Timer
from .utils import send_welcome_email
# views.py
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from threading import Timer
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import time
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .emails import send_welcome_email_async, send_welcome_email_task


import logging
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .emails import send_welcome_email_async, send_welcome_email_task  # ✅ import from emails.py

User = get_user_model()
logger = logging.getLogger(__name__)

@csrf_protect
@require_POST
def ajax_signup(request):
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    if not all([username, email, password]):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": "All fields are required."}, status=400)
        return redirect("index")

    if User.objects.filter(username=username).exists():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": "Username already taken."}, status=400)
        return redirect("index")

    if User.objects.filter(email=email).exists():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": "Email already registered."}, status=400)
        return redirect("index")

    # Create user + login
    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)

    # Try async email first, fallback to sync
    try:
        send_welcome_email_async(user.id)
    except Exception:
        send_welcome_email_task(user.id)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "message": "🎉 Registration successful! Welcome aboard."})

    return redirect("index")

# -------------------------------
# AJAX Login (email + optional password)
# -------------------------------
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def ajax_login(request):
    if request.method == "POST":
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            message = "Email and password are required."
            if is_ajax:
                return JsonResponse({"success": False, "message": message}, status=400)
            return redirect("index")

        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            message = "No account found with this email."
            if is_ajax:
                return JsonResponse({"success": False, "message": message}, status=400)
            return redirect("index")

        user_auth = authenticate(request, username=user.username, password=password)
        if not user_auth:
            message = "Invalid credentials."
            if is_ajax:
                return JsonResponse({"success": False, "message": message}, status=400)
            return redirect("index")

        # Successful login
        login(request, user_auth)
        message = "🎉 Login successful! Welcome back."
        if is_ajax:
            return JsonResponse({"success": True, "message": message})
        return redirect("index")

    # Fallback for non-POST requests
    return redirect("index")


@require_POST
@csrf_protect
def send_magic_link(request):
    email = request.POST.get("email", "").strip().lower()

    if not email:
        return JsonResponse({"ok": False, "errors": "Email is required."}, status=400)

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        # ✅ avoid leaking user existence, always return ok
        return JsonResponse({"ok": True})

    # ✅ generate secure token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # ✅ build link (magic_login must exist in urls.py)
    magic_path = reverse("magic_login")
    link = request.build_absolute_uri(f"{magic_path}?uid={uid}&token={token}")

    # ✅ send email
    try:
        send_mail(
            subject="Your Magic Login Link",
            message=f"""
Hello {user.username},

Click the link below to sign in securely:

{link}

⚠️ This link will expire in 15 minutes for your security.

If you didn’t request this login, please ignore this email.
            """,
            from_email="prospereze12345@gmail.com",  # ✅ your email
            recipient_list=[email],
            fail_silently=False,  # ❌ make it loud so you know if config fails
        )
    except Exception as e:
        return JsonResponse({"ok": False, "errors": f"Failed to send email: {str(e)}"}, status=500)

    return JsonResponse({"ok": True})


# -------------------------------
# Magic Login
# -------------------------------
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode

@csrf_protect
def magic_login(request):
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")

    if not uidb64 or not token:
        return JsonResponse({"error": "Invalid link"}, status=400)

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid, is_active=True)
    except Exception:
        return JsonResponse({"error": "Invalid link"}, status=400)

    if default_token_generator.check_token(user, token):
        login(request, user)
        return redirect("/")  # or wherever your dashboard is
    else:
        return JsonResponse({"error": "Link expired or invalid"}, status=400)


from django.contrib.auth.views import PasswordResetCompleteView

class ModalPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "password_reset_complete.html"  

    # override get_context_data to avoid reversing LOGIN_URL
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Instead of relying on LOGIN_URL, just pass a flag for modal login
        context['use_modal_login'] = True
        return context
