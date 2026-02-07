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


# --------------------------
# AJAX Signup
# --------------------------
@require_POST
@ensure_csrf_cookie
def ajax_signup(request):
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    # Validation
    if not all([username, email, password]):
        return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username already taken."}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "Email already registered."}, status=400)

    try:
        user = User.objects.create_user(username=username, email=email, password=password)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Failed to create user: {str(e)}"}, status=500)

    # Log in immediately
    login(request, user)

    # Send welcome email (fail silently)
    try:
        html_content = render_to_string("welcome_email.html", {"user": user})
        text_content = strip_tags(html_content)
        email_msg = EmailMultiAlternatives(
            subject="Welcome to EduPrompt 🎉",
            body=text_content,
            from_email="EduPrompt <prospereze12345@gmail.com>",
            to=[user.email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=True)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")

    return JsonResponse({"success": True, "message": "🎉 Registration successful! Welcome aboard."})


# --------------------------
# AJAX Login
# --------------------------
@require_POST
@ensure_csrf_cookie
def ajax_login(request):
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    if not all([email, password]):
        return JsonResponse({"success": False, "message": "Email and password are required."}, status=400)

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "No account found with this email."}, status=400)

    user_auth = authenticate(request, username=user.username, password=password)
    if not user_auth:
        return JsonResponse({"success": False, "message": "Invalid credentials."}, status=400)

    login(request, user_auth)
    return JsonResponse({"success": True, "message": "🎉 Login successful! Welcome back."})


# --------------------------
# Send Magic Link
# --------------------------
@require_POST
@ensure_csrf_cookie
def send_magic_link(request):
    email = request.POST.get("email", "").strip().lower()
    if not email:
        return JsonResponse({"ok": False, "errors": "Email is required."}, status=400)

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({"ok": True})  # Do not reveal user existence

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = request.build_absolute_uri(f"{reverse('magic_login')}?uid={uid}&token={token}")

    try:
        html_content = render_to_string("welcome_email.html", {"user": user, "magic_link": link})
        text_content = strip_tags(html_content)
        email_msg = EmailMultiAlternatives(
            subject="Your Magic Login Link",
            body=text_content,
            from_email="EduPrompt <prospereze12345@gmail.com>",
            to=[email]
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send(fail_silently=False)
    except Exception as e:
        return JsonResponse({"ok": False, "errors": f"Failed to send email: {str(e)}"}, status=500)

    return JsonResponse({"ok": True})


# --------------------------
# Magic Login
# --------------------------
@ensure_csrf_cookie
def magic_login(request):
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")
    if not uidb64 or not token:
        return JsonResponse({"error": "Invalid link"}, status=400)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid, is_active=True)
    except Exception:
        return JsonResponse({"error": "Invalid link"}, status=400)

    if default_token_generator.check_token(user, token):
        login(request, user)
        return redirect("/")  # Or your dashboard
    else:
        return JsonResponse({"error": "Link expired or invalid"}, status=400)
