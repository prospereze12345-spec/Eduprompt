from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import uuid
import requests
import logging
import docx
from PIL import Image
import pytesseract
from pypdf import PdfReader
from .models import UserProfile

logger = logging.getLogger(__name__)

# -------------------------
# Helpers
# -------------------------
def count_words(text):
    return len(text.split())

def extract_text_from_file(file_obj):
    ext = file_obj.name.split(".")[-1].lower()
    if ext == "docx":
        doc = docx.Document(file_obj)
        return " ".join([p.text for p in doc.paragraphs])
    elif ext == "pdf":
        reader = PdfReader(file_obj)
        return " ".join([page.extract_text() or "" for page in reader.pages])
    elif ext in ["jpg", "jpeg", "png"]:
        img = Image.open(file_obj)
        return pytesseract.image_to_string(img)
    else:
        return file_obj.read().decode(errors="ignore")

def run_languagetool_check(text, lang="en-US"):
    LT_URL = "https://api.languagetool.org/v2/check"
    try:
        response = requests.post(LT_URL, data={"text": text, "language": lang}, timeout=15)
        result = response.json()
        corrected_text = text
        highlighted_text = text
        suggestions_html = ""

        for match in sorted(result.get("matches", []), key=lambda m: m["offset"], reverse=True):
            message = match.get("message", "")
            offset = match.get("offset", 0)
            length = match.get("length", 0)
            replacements = match.get("replacements", [])
            replacement = replacements[0]["value"] if replacements else None

            if replacement:
                corrected_text = corrected_text[:offset] + replacement + corrected_text[offset+length:]

            highlighted_text = (
                highlighted_text[:offset] +
                f"<mark title='{message}'>" +
                highlighted_text[offset:offset+length] +
                "</mark>" +
                highlighted_text[offset+length:]
            )

            suggestions_html += f"<p>• {message}" + (f" → Suggestion: {replacement}" if replacement else "") + "</p>"

        return corrected_text, highlighted_text, suggestions_html

    except Exception as e:
        error_html = f"<p style='color:red;'>Grammar check failed: {e}</p>"
        return text, text, error_html

# -------------------------
# Grammar Checker View
# -------------------------
@csrf_exempt
@login_required
def grammar_checker(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        language = request.POST.get("language", "en-US")
        auto_correct = request.POST.get("auto_correct", "false") == "true"

        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)

        # -------------------------
        # Word limits
        # -------------------------
        WORD_LIMIT_FREE = 1500
        WORD_LIMIT_PRO = 5000
        is_pro = profile.is_subscribed and profile.subscription_end >= timezone.now()
        word_limit = WORD_LIMIT_PRO if is_pro else WORD_LIMIT_FREE
        word_count = count_words(text)

        if word_count > word_limit:
            msg = f"🚫 Word limit exceeded ({word_limit} words). Upgrade to Pro."
            return JsonResponse({"error": msg}, status=400)

        # -------------------------
        # Daily checks limits
        # -------------------------
        now = timezone.now()
        if not profile.last_check_date or profile.last_check_date.date() != now.date():
            profile.daily_check_count = 0
            profile.last_check_date = now

        max_checks = 50 if is_pro else 3
        if profile.daily_check_count >= max_checks:
            msg = f"⚠ Your daily limit of {max_checks} checks has been reached. Try again next day."
            return JsonResponse({"error": msg}, status=400)

        profile.daily_check_count += 1
        profile.last_check_date = now
        profile.save()

        # -------------------------
        # Supported languages
        # -------------------------
        supported_languages = [
            "af", "sw", "ar",
            "en-US", "en-GB", "en-AU", "en-CA", "en-NZ", "en-ZA",
            "fr", "fr-FR", "fr-CA", "fr-BE", "fr-CH",
            "de", "de-DE", "de-AT", "de-CH",
            "es", "es-ES", "es-MX", "es-AR", "es-CO", "es-CL",
            "it", "it-IT", "pt", "pt-PT", "pt-BR", "nl", "nl-NL", "nl-BE",
            "sv", "fi", "da", "no", "pl", "ru", "ro", "hu", "cs", "sk",
            "uk", "sl", "hr", "bg", "ja", "zh", "tr", "id"
        ]
        if language not in supported_languages:
            return JsonResponse({"error": f"Language '{language}' not supported"}, status=400)

        # -------------------------
        # Run LanguageTool
        # -------------------------
        corrected_text, highlighted_text, suggestions_html = run_languagetool_check(text, language)

        return JsonResponse({
            "corrected_text": corrected_text if auto_correct else None,
            "highlighted_text": highlighted_text,
            "suggestions_html": suggestions_html,
            "word_count": word_count,
            "daily_limit_remaining": max_checks - profile.daily_check_count,
            "source": "public_api"
        })

    return render(request, "grammar_checker.html")


# -------------------------
# File Upload Checker
# -------------------------
@csrf_exempt
@login_required
def grammar_upload_view(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        extracted_text = extract_text_from_file(file)
        word_count = count_words(extracted_text)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        is_pro = profile.is_subscribed and profile.subscription_end >= timezone.now()
        word_limit = 5000 if is_pro else 1500
        if word_count > word_limit:
            msg = "🚫 Limit exceeded. Max 5,000 words for Pro." if is_pro else "⚠ Free trial allows max 1,500 words. Upgrade to Pro."
            return JsonResponse({"success": False, "message": msg})

        # -------------------------
        # Daily check limits
        # -------------------------
        now = timezone.now()
        if not profile.last_check_date or profile.last_check_date.date() != now.date():
            profile.daily_check_count = 0
            profile.last_check_date = now

        max_checks = 50 if is_pro else 3
        if profile.daily_check_count >= max_checks:
            msg = f"⚠ Your daily limit of {max_checks} checks has been reached. Try again in 24 hours."
            return JsonResponse({"success": False, "message": msg}, status=400)

        profile.daily_check_count += 1
        profile.last_check_date = now
        profile.save()

        corrected_text, highlighted_text, suggestions_html = run_languagetool_check(extracted_text)

        return JsonResponse({
            "success": True,
            "words": word_count,
            "fixed_text": corrected_text,
            "highlighted_text": highlighted_text,
            "suggestions_html": suggestions_html,
            "message": "✅ Grammar check complete.",
            "daily_limit_remaining": max_checks - profile.daily_check_count
        })

    return JsonResponse({"success": False, "message": "No file uploaded"})


# -------------------------
# Subscription / Payment
# -------------------------
@login_required
def grammar_status(request):
    return render(request, "grammar_status.html", {"is_subscribed": getattr(request.user.userprofile, "is_subscribed", False)})

@login_required
def grammar_subscription_status(request):
    return JsonResponse({"is_subscribed": getattr(request.user.userprofile, "is_subscribed", False)})

def grammar_start_subscription(request):
    if not request.user.is_authenticated:
        return HttpResponse("""
            <script>
                alert("⚠ Please sign up or log in before subscribing.");
                if (window.bootstrap) {
                    var modalEl = document.getElementById("registerModal");
                    if (modalEl) { var modal = new bootstrap.Modal(modalEl); modal.show(); }
                }
                window.history.back();
            </script>
        """)

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    currency = request.GET.get("currency", "NGN")
    amount = 4000 if currency == "NGN" else 4
    tx_ref = f"grammar-{uuid.uuid4().hex[:10]}"
    user_profile.flutterwave_tx_ref = tx_ref
    user_profile.save()
    payment_options = "card,banktransfer,ussd,ngn,ussd_qr,eNaira" if currency == "NGN" else "card,applepay,googlepay,banktransfer"

    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": currency,
        "redirect_url": request.build_absolute_uri("/grammar-verify-subscription/"),
        "payment_options": payment_options,
        "customer": {"email": request.user.email or f"user{request.user.id}@example.com", "name": request.user.username},
        "customizations": {"title": "Grammar Pro Subscription", "description": "Unlock 50 checks per day and 5,000 words"}
    }
    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    try:
        res = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers, timeout=15)
        res_data = res.json()
        logger.info(f"Flutterwave grammar init: {res_data}")
    except requests.RequestException as e:
        logger.exception("Flutterwave request failed (grammar)")
        return JsonResponse({"error": f"Failed to initiate payment: {str(e)}"}, status=500)

    if res_data.get("status") == "success" and "link" in res_data.get("data", {}):
        return redirect(res_data["data"]["link"])
    return JsonResponse({"error": "Failed to initiate payment"}, status=400)

@login_required
def grammar_verify_subscription(request):
    tx_ref = request.GET.get("tx_ref")
    status = request.GET.get("status")
    if not tx_ref or not status:
        return redirect("/grammar-checker/")
    verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    res = requests.get(verify_url, headers=headers)
    res_data = res.json()
    if res_data.get("status") == "success":
        payment_status = res_data["data"].get("status", "").lower()
        if payment_status == "successful":
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
            user_profile.is_subscribed = True
            user_profile.subscription_start = timezone.now()
            user_profile.subscription_end = timezone.now() + timedelta(days=30)
            user_profile.flutterwave_tx_ref = tx_ref
            user_profile.save()
            return redirect("/grammar-checker/?subscribed=1")
    return redirect("/grammar-checker/?subscribed=0")













    
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .improve import (
    AcademicToneImprover,
    CVImprover,
    ProfessionalEmailImprover,
    TextSummarizer
)


@csrf_exempt
def improve_text(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()
        goal = data.get("goal", "academic").lower()

        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)

        # ================= ROUTING BASED ON GOAL =================
        result_obj = None

        if goal == "academic":
            improver = AcademicToneImprover()
            result_obj = improver.improve(text)

        elif goal == "cv":
            industry = data.get("industry", "general")
            improver = CVImprover()
            result_obj = improver.improve(text, industry)

        elif goal == "email":
            email_type = data.get("email_type", "general")
            email_tone = data.get("email_tone", "semi_formal")
            improver = ProfessionalEmailImprover()
            result_obj = improver.improve(text, email_type, email_tone)

        # Accept both spellings: "summarize" (US) or "summarise" (UK)
        elif goal in ["summarize", "summarise"]:
            improver = TextSummarizer()
            result_obj = improver.improve(text)

        else:
            return JsonResponse({"error": f"Invalid goal: {goal}"}, status=400)

        # ================= PICK THE IMPROVED TEXT =================
        if isinstance(result_obj, dict) and "improved" in result_obj:
            result_text = result_obj["improved"]
        elif isinstance(result_obj, str):
            result_text = result_obj
        else:
            result_text = str(result_obj)

        return JsonResponse({
            "success": True,
            "result": result_text  # just the improved text
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    



import io
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def extract_file_text(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".txt"):
            # Read text file
            text = uploaded_file.read().decode("utf-8", errors="ignore")

        elif file_name.endswith(".pdf"):
            # Wrap uploaded_file in BytesIO to make PdfReader happy
            pdf_bytes = uploaded_file.read()
            pdf_file = io.BytesIO(pdf_bytes)

            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            if not text.strip():
                return JsonResponse({
                    "error": "PDF has no readable text. Maybe it's scanned or image-based."
                }, status=400)
        else:
            return JsonResponse({"error": "Unsupported file type"}, status=400)

        return JsonResponse({"success": True, "text": text})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)