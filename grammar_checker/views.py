from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests


from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
import requests

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests

@csrf_exempt
@login_required
def grammar_checker(request):
    """
    Grammar checker using self-hosted LanguageTool only.
    Supports many languages including African ones (af, sw, ar).
    Integrates with user subscription to allow Pro users to check up to 15k+ words.
    Requires user login before checking grammar.
    """
    if request.method == "POST":
        user = request.user

        text = request.POST.get("text", "").strip()
        language = request.POST.get("language", "en-US")  # default English
        auto_correct = request.POST.get("auto_correct", "false") == "true"

        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)

        # --- Word limits ---
        WORD_LIMIT_FREE = 2000   # Free trial: 2k words
        WORD_LIMIT_PRO = 15000   # Pro users: 15k words

        # --- Subscription check ---
        word_limit = WORD_LIMIT_FREE
        if hasattr(user, "userprofile"):
            profile = user.userprofile
            if profile.is_subscribed and profile.subscription_end:
                if profile.subscription_end >= timezone.now():
                    word_limit = WORD_LIMIT_PRO
                else:
                    # Expired → reset subscription
                    profile.is_subscribed = False
                    profile.save()

        word_count = len(text.split())
        if word_count > word_limit:
            return JsonResponse({
                "error": f"Word limit exceeded ({word_limit} words). Upgrade to Pro for more."
            }, status=400)

        # --- Supported languages ---
        supported_languages = [
            # African languages
            "af", "sw", "ar",
            # English
            "en-US", "en-GB", "en-AU", "en-CA", "en-NZ", "en-ZA",
            # French
            "fr", "fr-FR", "fr-CA", "fr-BE", "fr-CH",
            # German
            "de", "de-DE", "de-AT", "de-CH",
            # Spanish
            "es", "es-ES", "es-MX", "es-AR", "es-CO", "es-CL",
            # Other languages
            "it", "it-IT", "pt", "pt-PT", "pt-BR", "nl", "nl-NL", "nl-BE",
            "sv", "fi", "da", "no", "pl", "ru", "ro", "hu", "cs", "sk",
            "uk", "sl", "hr", "bg", "ja", "zh", "tr", "id"
        ]
        if language not in supported_languages:
            return JsonResponse({"error": f"Language '{language}' not supported"}, status=400)

        try:
            # --- Call self-hosted LanguageTool ---
            lt_response = requests.post(
                settings.LANGUAGETOOL_API,
                data={"text": text, "language": language},
                timeout=30
            )
            lt_response.raise_for_status()
            lt_data = lt_response.json()
            matches = lt_data.get("matches", [])

            corrected_text = text
            if auto_correct and matches:
                corrected_chars = list(text)
                shift = 0
                for match in matches:
                    replacements = match.get("replacements", [])
                    if replacements:
                        repl = replacements[0]["value"]
                        offset = match["offset"] + shift
                        length = match["length"]
                        corrected_chars[offset:offset+length] = list(repl)
                        shift += len(repl) - length
                corrected_text = "".join(corrected_chars)

            return JsonResponse({
                "matches": matches,
                "corrected_text": corrected_text if auto_correct else None,
                "source": "lt"
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"LanguageTool API request failed: {e}"}, status=500)

    # --- GET request: render HTML ---
    return render(request, "grammar_checker.html")



import uuid
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@login_required
def grammar_status(request):
    """Render a simple subscription status page (for debugging / display)."""
    return render(request, "grammar_status.html", {
        "is_subscribed": getattr(request.user.userprofile, "is_subscribed", False)
    })


@login_required
def grammar_subscription_status(request):
    """AJAX endpoint for frontend to check subscription status."""
    return JsonResponse({
        "is_subscribed": getattr(request.user.userprofile, "is_subscribed", False)
    })
from datetime import timedelta
from django.utils import timezone
import uuid
import requests
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserProfile

@login_required
def grammar_start_subscription(request):
    """Start Flutterwave payment for Grammar Pro subscription (30 days)."""

    # ✅ Ensure profile exists for this user
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Detect currency (default = NGN)
    currency = request.GET.get("currency", "NGN")
    amount = 3500 if currency == "NGN" else 6  # one flat price plan

    # Generate unique transaction ref
    tx_ref = f"grammar-{uuid.uuid4().hex[:10]}"
    user_profile.flutterwave_tx_ref = tx_ref
    user_profile.save()

    # Flutterwave payment payload
    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": currency,
        "redirect_url": request.build_absolute_uri("/grammar-verify-subscription/"),
        "payment_options": "card,banktransfer",
        "customer": {
            "email": request.user.email,
            "name": request.user.username,
        },
        "customizations": {
            "title": "Grammar Pro Subscription",
            "description": "Unlock 15k+ words for 30 days",
        }
    }

    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    res = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers)
    res_data = res.json()

    if res_data.get("status") == "success":
        return redirect(res_data["data"]["link"])

    return JsonResponse({"error": "Failed to initiate payment"}, status=400)
from datetime import timedelta
from django.utils import timezone
import requests
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def grammar_verify_subscription(request):
    """Flutterwave redirects here after payment to verify transaction."""
    tx_ref = request.GET.get("tx_ref")
    status = request.GET.get("status")

    if not tx_ref or not status:
        return redirect("/grammar-checker/")

    # Verify with Flutterwave API
    verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}  # ✅ use correct key
    res = requests.get(verify_url, headers=headers)
    res_data = res.json()

    if res_data.get("status") == "success":
        payment_status = res_data["data"].get("status", "").lower()
        if payment_status == "successful":
            # ✅ Ensure profile exists
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
            user_profile.is_subscribed = True
            user_profile.subscription_start = timezone.now()
            user_profile.subscription_end = timezone.now() + timedelta(days=30)  # expires in 30 days
            user_profile.flutterwave_tx_ref = tx_ref
            user_profile.save()
            return redirect("/grammar-checker/?subscribed=1")

    return redirect("/grammar-checker/?subscribed=0")

import docx
import pytesseract
from PIL import Image
from pypdf import PdfReader
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserProfile
import requests

# --- helpers ---
def count_words(text):
    return len(text.split())

def extract_text_from_file(file_obj):
    ext = file_obj.name.split(".")[-1].lower()

    if ext in ["docx"]:
        doc = docx.Document(file_obj)
        return " ".join([p.text for p in doc.paragraphs])

    elif ext in ["pdf"]:
        reader = PdfReader(file_obj)
        return " ".join([page.extract_text() or "" for page in reader.pages])

    elif ext in ["jpg", "jpeg", "png"]:
        img = Image.open(file_obj)
        return pytesseract.image_to_string(img)

    else:
        return file_obj.read().decode(errors="ignore")

def run_languagetool_check(text):
    """Send text to self-hosted LanguageTool server and return corrected text and suggestions."""
    LT_URL = "http://127.0.0.1:8010/v2/check"  # adjust port if needed
    try:
        response = requests.post(
            LT_URL,
            data={
                "text": text,
                "language": "en-US"
            },
            timeout=15
        )
        result = response.json()
        # Apply simple replacements for corrected text
        corrected_text = text
        suggestions_html = ""
        for match in result.get("matches", []):
            message = match.get("message", "")
            context = match.get("context", {})
            offset = context.get("offset", 0)
            length = context.get("length", 0)
            replacement = match.get("replacements")[0]["value"] if match.get("replacements") else None
            if replacement:
                # Replace in corrected_text
                corrected_text = corrected_text[:offset] + replacement + corrected_text[offset+length:]
            suggestions_html += f"<p>• {message}</p>"

        return corrected_text, suggestions_html
    except Exception as e:
        return text, f"<p style='color:red;'>Grammar check failed: {e}</p>"

# --- view ---
@login_required
def grammar_upload_view(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        extracted_text = extract_text_from_file(file)
        word_count = count_words(extracted_text)

        # ensure profile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        # subscription logic
        limit = 15000 if profile.is_subscribed else 2000
        if word_count > limit:
            msg = "🚫 Limit exceeded. Max 15,000 words per file." if profile.is_subscribed else \
                  "⚠ Free trial allows max 2,000 words. Subscribe to unlock 15k words."
            return JsonResponse({"success": False, "message": msg})

        # run LanguageTool grammar check
        corrected_text, suggestions_html = run_languagetool_check(extracted_text)

        # return JSON
        return JsonResponse({
            "success": True,
            "words": word_count,
            "fixed_text": corrected_text,
            "suggestions_html": suggestions_html
        })

    return JsonResponse({"success": False, "message": "No file uploaded"})
