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
## AJAX / NORMAL SIGNUP (Production Ready)
# --------------------------
from django.db import IntegrityError
import traceback
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth import login, get_user_model
from users.emails import send_welcome_email_async  # <-- import your async email

User = get_user_model()
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from .emails import send_welcome_email_async  # your existing email function
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import login
from django.views.decorators.http import require_POST
@require_POST
def ajax_signup(request):
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    # --------------------------
    # Honeypot check to block bots
    # --------------------------
    honeypot = request.POST.get("honeypot", "")
    if honeypot:  # If field is filled, likely a bot
        return JsonResponse({"error": "Bot detected!"}, status=400)

    if not all([username, email, password]):
        return JsonResponse({"error": "All fields are required."}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already taken."}, status=400)

    # --------------------------
    # Handle duplicate email gracefully
    # --------------------------
    existing_user = User.objects.filter(email=email).first()
    if existing_user:
        return JsonResponse({"error": "Email already registered. Please log in instead."}, status=400)

    try:
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        # --------------------------
        # Send welcome email asynchronously
        # --------------------------
        if user.email:
            send_welcome_email_async(user.id)

    except IntegrityError:
        # Rare case: race condition / duplicate creation
        return JsonResponse({"error": "Email already registered. Please log in instead."}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Failed to create user: {str(e)}"}, status=500)

    # --------------------------
    # Redirect to homepage after successful signup
    # --------------------------
    return redirect("/")


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse
from .models import MagicLoginToken
import resend

# Initialize Resend API
resend.api_key = settings.RESEND_API_KEY

def send_magic_link(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    email = request.POST.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Create token
    token = MagicLoginToken.objects.create(user=user)

    # Build the magic login URL
    login_url = request.build_absolute_uri(
        reverse("magic_login", args=[str(token.token)])
    )

    # Send magic link via Resend
    sender_email = settings.DEFAULT_FROM_EMAIL
    try:
        resend.Emails.send({
            "from": sender_email,
            "to": email,
            "subject": "Your Smart Login Link",
            "html": f"""
                <h2>Smart Login</h2>
                <p>Click the button below to login:</p>
                <a href="{login_url}" 
                   style="padding:10px 20px;background:#2563eb;color:white;
                          text-decoration:none;border-radius:5px;">
                   Login Now
                </a>
                <p>This link expires in 10 minutes.</p>
            """
        })
    except Exception as e:
        token.delete()
        return JsonResponse({"error": f"Failed to send email: {str(e)}"}, status=500)

    # Return success for AJAX popup
    return JsonResponse({"success": "Magic link sent! Check your email 🔥"})

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import login
from .models import MagicLoginToken

def magic_login(request, token):
    token_obj = get_object_or_404(MagicLoginToken, token=token)

    if token_obj.is_expired():
        token_obj.delete()
        # Redirect to login page with query param for popup
        return redirect(f"/login/?error=Link+expired")

    # Log in the user
    login(request, token_obj.user)
    token_obj.delete()  # Prevent reuse

    # Redirect to homepage with query param for success popup
    return redirect(f"/?success=Logged+in+successfully")
from django.urls import path
from django.http import JsonResponse

def health_check(request):
    """
    Simple health check endpoint.
    Used for monitoring and warming up the app.
    """
    return JsonResponse({"status": "ok", "message": "I'm awake!"})
