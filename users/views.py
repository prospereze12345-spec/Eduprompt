# views.py
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

User = get_user_model()

@csrf_protect
@require_POST
def ajax_signup(request):
    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    # Validate required fields
    if not all([username, email, password]):
        return JsonResponse({"success": False, "message": "All fields are required."}, status=400) if is_ajax else redirect("index")

    # Check username/email uniqueness
    if User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Username already taken."}, status=400) if is_ajax else redirect("index")
    if User.objects.filter(email=email).exists():
        return JsonResponse({"success": False, "message": "Email already registered."}, status=400) if is_ajax else redirect("index")

    # Create user and login
    user = User.objects.create_user(username=username, email=email, password=password)
    login(request, user)

    # Send HTML welcome email
    try:
        html_content = render_to_string("welcome_email.html", {"user": user})
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            subject="Welcome to EduPrompt 🎉",
            body=text_content,
            from_email="EduPrompt <prospereze12345@gmail.com>",
            to=[user.email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")

    return JsonResponse({"success": True, "message": "🎉 Registration successful! Welcome aboard."}) if is_ajax else redirect("index")


@csrf_protect
@require_POST
def ajax_login(request):
    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "").strip()
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if not all([email, password]):
        return JsonResponse({"success": False, "message": "Email and password are required."}, status=400) if is_ajax else redirect("index")

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "No account found with this email."}, status=400) if is_ajax else redirect("index")

    user_auth = authenticate(request, username=user.username, password=password)
    if not user_auth:
        return JsonResponse({"success": False, "message": "Invalid credentials."}, status=400) if is_ajax else redirect("index")

    login(request, user_auth)
    return JsonResponse({"success": True, "message": "🎉 Login successful! Welcome back."}) if is_ajax else redirect("index")


@csrf_protect
@require_POST
def send_magic_link(request):
    email = request.POST.get("email", "").strip().lower()
    if not email:
        return JsonResponse({"ok": False, "errors": "Email is required."}, status=400)

    try:
        user = User.objects.get(email__iexact=email, is_active=True)
    except User.DoesNotExist:
        return JsonResponse({"ok": True})  # Avoid revealing user existence

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    link = request.build_absolute_uri(f"{reverse('magic_login')}?uid={uid}&token={token}")

    try:
        html_content = render_to_string("welcome_email.html", {"user": user, "magic_link": link})
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            subject="Your Magic Login Link",
            body=text_content,
            from_email="EduPrompt <prospereze12345@gmail.com>",
            to=[email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)
    except Exception as e:
        return JsonResponse({"ok": False, "errors": f"Failed to send email: {str(e)}"}, status=500)

    return JsonResponse({"ok": True})


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
        return redirect("/")  # Change to your dashboard
    else:
        return JsonResponse({"error": "Link expired or invalid"}, status=400)
