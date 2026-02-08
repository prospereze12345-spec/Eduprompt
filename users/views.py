from django.contrib.auth import login, authenticate, get_user_model
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.shortcuts import redirect


User = get_user_model()
from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

User = get_user_model()
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
import traceback
# --------------------------
# AJAX / NORMAL SIGNUP (Production Ready)
# --------------------------
from django.db import IntegrityError
import traceback

@require_POST
def ajax_signup(request):
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    if not all([username, email, password]):
        return JsonResponse({"success": False, "errors": "All fields are required."}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "errors": "Username already taken."}, status=400)

    # --------------------------
    # Handle duplicate email gracefully
    # --------------------------
    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        return JsonResponse({
            "success": False,
            "errors": "Email already registered. Please log in instead."
        }, status=400)

    try:
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

    except IntegrityError:
        # Rare case: race condition / duplicate creation
        return JsonResponse({
            "success": False,
            "errors": "Email already registered. Please log in instead."
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "errors": f"Failed to create user: {str(e)}"
        }, status=500)

    # --------------------------
    # AJAX response
    # --------------------------
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "redirect_url": "/"})

    return redirect("/")




# --------------------------
# AJAX / NORMAL LOGIN
# --------------------------
@require_POST
def ajax_login(request):
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    if not all([email, password]):
        return JsonResponse({"success": False, "errors": "Email and password are required."})

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "errors": "Invalid credentials."})

    user_auth = authenticate(request, username=user.username, password=password)
    if not user_auth:
        return JsonResponse({"success": False, "errors": "Invalid credentials."})

    login(request, user_auth)

    # AJAX detection and redirect
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": True, "redirect_url": "/"})

    return redirect("/")


# --------------------------
# SEND MAGIC LINK (AJAX + NORMAL)
# --------------------------
@require_POST
def send_magic_link(request):
    email = request.POST.get("email", "").strip().lower()
    if not email:
        return JsonResponse({"ok": False, "errors": "Email is required."}, status=400)

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        # Do not reveal user existence
        return JsonResponse({"ok": True})

    # Generate token and magic login link
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    magic_link = request.build_absolute_uri(f"{reverse('magic_login')}?uid={uid}&token={token}")

    # Send email
    try:
        html_content = render_to_string("welcome_email.html", {"user": user, "magic_link": magic_link})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject="Your Magic Login Link",
            body=text_content,
            from_email="EduPrompt <prospereze12345@gmail.com>",
            to=[email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
    except Exception as e:
        return JsonResponse({"ok": False, "errors": f"Failed to send email: {str(e)}"}, status=500)

    return JsonResponse({"ok": True, "magic_link": magic_link})


# --------------------------
# MAGIC LOGIN
# --------------------------
def magic_login(request):
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")

    if not uidb64 or not token:
        return redirect("/")

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid, is_active=True)
    except Exception:
        return redirect("/")

    # Check token validity
    if default_token_generator.check_token(user, token):
        login(request, user)
        # Redirect to homepage or dashboard after successful magic login
        return redirect("/")

    # Token invalid or expired
    return redirect("/")








from django.urls import path
from django.http import JsonResponse

def health_check(request):
    """
    Simple health check endpoint.
    Used for monitoring and warming up the app.
    """
    return JsonResponse({"status": "ok", "message": "I'm awake!"})
