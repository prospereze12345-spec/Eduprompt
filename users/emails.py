# users/emails.py
import logging
from threading import Thread
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def send_welcome_email_task(user_id):
    """
    Fetch user and send the welcome email synchronously.
    Returns True if sent, False otherwise.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("❌ User with id=%s not found.", user_id)
        return False

    try:
        html_content = render_to_string("emails/welcome_email.html", {"user": user})
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject="Welcome to Eduprompt!",
            body=text_content,
            from_email="eduprompt@outlook.com",  # ✅ verified SendGrid sender
            to=[user.email],
            reply_to=["eduprompt@outlook.com"],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info("✅ Welcome email sent to %s (%s)", user.username, user.email)
        return True
    except Exception as exc:
        logger.exception("❌ Error sending welcome email to %s: %s", getattr(user, "email", user_id), exc)
        return False


def send_welcome_email_async(user_id):
    """
    Run the welcome email in a background thread.
    If thread fails, the caller should fallback to sync.
    """
    try:
        thread = Thread(target=send_welcome_email_task, args=(user_id,), daemon=True)
        thread.start()
        logger.info("📨 Email thread started for user_id=%s", user_id)
    except Exception as exc:
        logger.exception("❌ Failed to start email thread for user %s: %s", user_id, exc)
        raise  # let caller handle fallback



# users/views.py
import logging
from django.contrib.auth import login, get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .emails import send_welcome_email_async, send_welcome_email_task  # ✅

logger = logging.getLogger(__name__)
User = get_user_model()


@csrf_protect
@require_POST
def ajax_signup(request):
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    # Validate inputs
    if not all([username, email, password]):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": "All fields are required."}, status=400)
        return redirect("index")

    # Check uniqueness
    if User.objects.filter(username=username).exists():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": "Username already taken."}, status=400)
        return redirect("index")

    if User.objects.filter(email=email).exists():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": "Email already registered."}, status=400)
        return redirect("index")

    # Create user and login
    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)

    # Try async email, fallback to sync
    try:
        send_welcome_email_async(user.id)
        logger.info("✅ Async welcome email started for %s", user.email)
    except Exception as exc:
        logger.exception("⚠️ Async email failed for %s: %s", user.email, exc)
        try:
            send_welcome_email_task(user.id)
        except Exception as inner_exc:
            logger.exception("❌ Sync fallback email also failed for %s: %s", user.email, inner_exc)

    # Return JSON response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True, "message": "🎉 Registration successful! Welcome aboard."})

    return redirect("index")
