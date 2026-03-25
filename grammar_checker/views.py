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
# Imports
# -------------------------
import re
import requests
import docx
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone


# -------------------------
# Helpers
# -------------------------
def count_words(text):
    return len(text.split())


def normalize_text(text):
    """
    Clean common formatting problems before grammar analysis.
    Reduces quote-related warnings from LanguageTool.
    """

    text = text.replace("''", '"')
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_text_from_file(file_obj):
    ext = file_obj.name.split(".")[-1].lower()

    if ext == "docx":
        doc = docx.Document(file_obj)
        return " ".join(p.text for p in doc.paragraphs)

    elif ext == "pdf":
        reader = PdfReader(file_obj)
        return " ".join(page.extract_text() or "" for page in reader.pages)

    elif ext in ["jpg", "jpeg", "png"]:
        img = Image.open(file_obj)
        return pytesseract.image_to_string(img)

    else:
        return file_obj.read().decode(errors="ignore")

def detect_repeated_words(text):
    issues = []

    for m in re.finditer(r"\b(\w+)\s+\1\b", text, re.IGNORECASE):

        issues.append({
            "start": m.start(),
            "end": m.end(),
            "message": "Repeated word detected"
        })

    return issues


def detect_passive_voice(text):
    """
    Detect clearer passive constructions only
    to avoid excessive warnings.
    """

    issues = []

    pattern = r"\b(is|was|were|are|been|being)\s+\w+ed\s+by\b"

    for m in re.finditer(pattern, text, re.IGNORECASE):

        issues.append({
            "start": m.start(),
            "end": m.end(),
            "message": "Possible passive voice. Consider using active voice."
        })

    return issues


def detect_weak_words(text):

    issues = []

    weak_words = [
        "very",
        "really",
        "things",
        "stuff",
        "a lot",
        "kind of",
        "sort of",
        "basically",
        "actually",
        "quite",
        "somewhat",
        "maybe"
    ]

    pattern = r"\b(" + "|".join(map(re.escape, weak_words)) + r")\b"

    for m in re.finditer(pattern, text, re.IGNORECASE):

        issues.append({
            "start": m.start(),
            "end": m.end(),
            "message": f"Weak word '{m.group()}' detected. Consider a stronger word."
        })

    return issues


def detect_long_sentences(text):

    issues = []

    for m in re.finditer(r"[^.!?]+[.!?]", text):

        sentence = m.group()

        if len(sentence.split()) > 30:

            issues.append({
                "start": m.start(),
                "end": m.end(),
                "message": "Sentence too long. Consider splitting."
            })

    return issues


def run_extra_nlp_checks(text):

    issues = []

    issues += detect_repeated_words(text)
    issues += detect_passive_voice(text)
    issues += detect_weak_words(text)
    issues += detect_long_sentences(text)

    # keep highlights consistent
    issues = sorted(issues, key=lambda x: x["start"])

    return issues


# -------------------------
# Duplicate Detection
# -------------------------
def overlaps(new_issue, existing_issues):

    for issue in existing_issues:

        overlap = not (
            new_issue["end"] <= issue["start"] or
            new_issue["start"] >= issue["end"]
        )

        if overlap:
            return True

    return False


# -------------------------
# LanguageTool + NLP Engine
# -------------------------
def run_languagetool_check(text, lang="en-US"):

    text = normalize_text(text)

    LT_URL = "https://api.languagetool.org/v2/check"

    try:

        response = requests.post(
            LT_URL,
            data={"text": text, "language": lang},
            timeout=15
        )

        result = response.json()

        corrected_text = text
        highlighted_text = text
        suggestions_html = ""

        lt_issues = []

        # -------------------------
        # Process LanguageTool results
        # -------------------------
        for match in sorted(result.get("matches", []), key=lambda m: m["offset"], reverse=True):

            message = match.get("message", "")
            offset = match.get("offset", 0)
            length = match.get("length", 0)

            replacements = match.get("replacements", [])
            replacement = replacements[0]["value"] if replacements else None

            start = offset
            end = offset + length

            lt_issues.append({"start": start, "end": end})

            if replacement:
                corrected_text = corrected_text[:start] + replacement + corrected_text[end:]

            highlighted_text = (
                highlighted_text[:start]
                + f"<mark title='{message}'>"
                + highlighted_text[start:end]
                + "</mark>"
                + highlighted_text[end:]
            )

            suggestions_html += f"<p>• {message}"
            if replacement:
                suggestions_html += f" → Suggestion: {replacement}"
            suggestions_html += "</p>"

        # -------------------------
        # Run extra NLP rules
        # -------------------------
        nlp_issues = run_extra_nlp_checks(text)

        for issue in nlp_issues:

            if not overlaps(issue, lt_issues):

                start = issue["start"]
                end = issue["end"]
                message = issue["message"]

                highlighted_text = (
                    highlighted_text[:start]
                    + f"<mark style='background:#ffeaa7' title='{message}'>"
                    + highlighted_text[start:end]
                    + "</mark>"
                    + highlighted_text[end:]
                )

                suggestions_html += f"<p>• {message}</p>"

        return corrected_text, highlighted_text, suggestions_html

    except Exception as e:

        error_html = f"<p style='color:red;'>Grammar check failed: {e}</p>"
        return text, text, error_html
# top of your views.py
import os
import redis as redis_lib
import hashlib
import json
from datetime import date
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from upstash_redis import Redis
import os

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
)
# -------------------------
# HELPER: SAFE CACHE
# -------------------------
def get_cache(key):
    try:
        data = redis.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None  # fallback


def set_cache(key, value, expiry=3600):
    try:
        redis.set(key, json.dumps(value), ex=expiry)
    except Exception:
        pass  # never break app


# -------------------------
# HELPER: TRACK ANALYTICS
# -------------------------
def track_analytics(user_part, text):
    try:
        # Total requests
        redis.incr("stats:total_requests")
        # Requests per user/IP
        redis.incr(f"stats:user:{user_part}")
        # Popular queries (sorted set)
        query_hash = hashlib.md5(text.encode()).hexdigest()
        redis.zincrby("stats:popular_queries", 1, query_hash)
        # Map hash → actual text (expires in 1 day)
        redis.set(f"query_map:{query_hash}", text, ex=86400)
    except Exception:
        pass  # fallback


# -------------------------
# Grammar Checker View
# -------------------------
@csrf_exempt
def grammar_checker(request):
    user = request.user
    is_guest = not user.is_authenticated
    profile = None

    if not is_guest:
        profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        auto_correct = request.POST.get("auto_correct", "false") == "true"

        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)

        WORD_LIMIT_FREE = 1500
        WORD_LIMIT_PRO = 5000
        is_pro = False if is_guest else (
            profile.is_subscribed and profile.subscription_end >= timezone.now()
        )
        word_limit = WORD_LIMIT_PRO if is_pro else WORD_LIMIT_FREE
        word_count = count_words(text)

        if word_count > word_limit:
            return JsonResponse(
                {"error": f"🚫 Word limit exceeded ({word_limit}). Upgrade to Pro."},
                status=400
            )

        # -------------------------
        # DAILY LIMIT LOGIC (UNCHANGED)
        # -------------------------
        if is_guest:
            today = str(date.today())
            last_trial_date = request.session.get("grammar_trial_date")
            trials = request.session.get("grammar_trials", 0)

            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = ip.split(',')[0] if ip else request.META.get('REMOTE_ADDR')

            ip_trial_key = f"grammar_ip_trials_{ip}"
            ip_date_key = f"grammar_ip_date_{ip}"

            ip_trials = request.session.get(ip_trial_key, 0)
            ip_date = request.session.get(ip_date_key)

            if last_trial_date != today:
                trials = 0
                request.session["grammar_trials"] = 0
                request.session["grammar_trial_date"] = today

            if ip_date != today:
                ip_trials = 0
                request.session[ip_trial_key] = 0
                request.session[ip_date_key] = today

            if trials >= 3 or ip_trials >= 3:
                return JsonResponse(
                    {"error": "⚠ Free daily limit reached. Sign up for more checks."},
                    status=400
                )

            request.session["grammar_trials"] = trials + 1
            request.session[ip_trial_key] = ip_trials + 1
            remaining = 3 - request.session["grammar_trials"]

            user_part = ip

        else:
            now = timezone.now()
            if not profile.last_check_date or profile.last_check_date.date() != now.date():
                profile.daily_check_count = 0
                profile.last_check_date = now

            max_checks = 50 if is_pro else 3

            if profile.daily_check_count >= max_checks:
                return JsonResponse(
                    {"error": f"⚠ Daily limit of {max_checks} checks reached."},
                    status=400
                )

            profile.daily_check_count += 1
            profile.save()
            remaining = max_checks - profile.daily_check_count

            user_part = str(user.id)

        # -------------------------
        # CACHE KEY
        # -------------------------
        language = "auto"
        cache_key = "grammar:" + hashlib.md5((text + str(auto_correct) + user_part).encode()).hexdigest()

        # -------------------------
        # TRY CACHE
        # -------------------------
        cached = get_cache(cache_key)
        if cached:
            return JsonResponse({
                "corrected_text": cached.get("corrected_text") if auto_correct else None,
                "highlighted_text": cached.get("highlighted_text"),
                "suggestions_html": cached.get("suggestions_html"),
                "word_count": word_count,
                "daily_limit_remaining": remaining,
                "cached": True
            })

        # -------------------------
        # FALLBACK → LANGUAGE TOOL
        # -------------------------
        corrected_text, highlighted_text, suggestions_html = run_languagetool_check(text, language)

        # -------------------------
        # SAVE CACHE
        # -------------------------
        set_cache(cache_key, {
            "corrected_text": corrected_text,
            "highlighted_text": highlighted_text,
            "suggestions_html": suggestions_html
        })

        # -------------------------
        # TRACK ANALYTICS
        # -------------------------
        track_analytics(user_part, text)

        return JsonResponse({
            "corrected_text": corrected_text if auto_correct else None,
            "highlighted_text": highlighted_text,
            "suggestions_html": suggestions_html,
            "word_count": word_count,
            "daily_limit_remaining": remaining,
            "cached": False
        })

    return render(request, "grammar_checker.html")


# -------------------------
# File Upload Checker
# -------------------------
@csrf_exempt
def grammar_upload_view(request):
    if request.method == "POST" and request.FILES.get("file"):

        file = request.FILES["file"]
        extracted_text = extract_text_from_file(file)
        word_count = count_words(extracted_text)

        user = request.user
        is_guest = not user.is_authenticated
        profile = None
        if not is_guest:
            profile, _ = UserProfile.objects.get_or_create(user=user)

        WORD_LIMIT_FREE = 1500
        WORD_LIMIT_PRO = 5000
        is_pro = False if is_guest else (
            profile.is_subscribed and profile.subscription_end >= timezone.now()
        )
        word_limit = WORD_LIMIT_PRO if is_pro else WORD_LIMIT_FREE

        if word_count > word_limit:
            return JsonResponse({
                "success": False,
                "message": "🚫 Max 5,000 words for Pro." if is_pro else "⚠ Free limit 1,500 words."
            })

        # DAILY LIMIT LOGIC SAME AS ABOVE
        if is_guest:
            today = str(date.today())
            last_trial_date = request.session.get("grammar_trial_date")
            trials = request.session.get("grammar_trials", 0)

            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = ip.split(',')[0] if ip else request.META.get('REMOTE_ADDR')

            ip_trial_key = f"grammar_ip_trials_{ip}"
            ip_date_key = f"grammar_ip_date_{ip}"

            ip_trials = request.session.get(ip_trial_key, 0)
            ip_date = request.session.get(ip_date_key)

            if last_trial_date != today:
                trials = 0
                request.session["grammar_trials"] = 0
                request.session["grammar_trial_date"] = today

            if ip_date != today:
                ip_trials = 0
                request.session[ip_trial_key] = 0
                request.session[ip_date_key] = today

            if trials >= 3 or ip_trials >= 3:
                return JsonResponse({
                    "success": False,
                    "message": "⚠ Free daily limit reached. Sign up for more checks."
                })

            request.session["grammar_trials"] = trials + 1
            request.session[ip_trial_key] = ip_trials + 1
            user_part = ip

        else:
            now = timezone.now()
            if not profile.last_check_date or profile.last_check_date.date() != now.date():
                profile.daily_check_count = 0
                profile.last_check_date = now

            max_checks = 50 if is_pro else 3
            if profile.daily_check_count >= max_checks:
                return JsonResponse({
                    "success": False,
                    "message": f"⚠ Daily limit of {max_checks} checks reached."
                })

            profile.daily_check_count += 1
            profile.save()
            user_part = str(user.id)

        # CACHE
        language = "auto"
        cache_key = "upload:" + hashlib.md5((extracted_text + user_part).encode()).hexdigest()
        cached = get_cache(cache_key)
        if cached:
            return JsonResponse({
                "success": True,
                "words": word_count,
                "fixed_text": cached.get("corrected_text"),
                "highlighted_text": cached.get("highlighted_text"),
                "suggestions_html": cached.get("suggestions_html"),
                "cached": True
            })

        # FALLBACK
        corrected_text, highlighted_text, suggestions_html = run_languagetool_check(extracted_text, language)

        # SAVE CACHE
        set_cache(cache_key, {
            "corrected_text": corrected_text,
            "highlighted_text": highlighted_text,
            "suggestions_html": suggestions_html
        })

        track_analytics(user_part, extracted_text)

        return JsonResponse({
            "success": True,
            "words": word_count,
            "fixed_text": corrected_text,
            "highlighted_text": highlighted_text,
            "suggestions_html": suggestions_html,
            "cached": False
        })

    return JsonResponse({"success": False, "message": "No file uploaded"})

@login_required
def grammar_status(request):
    return render(request, "grammar_status.html", {"is_subscribed": getattr(request.user.userprofile, "is_subscribed", False)})
import uuid
import requests
import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from upstash_redis import Redis
from django.conf import settings

logger = logging.getLogger(__name__)

# -------------------------
# Redis setup for locks/rate limiting
# -------------------------

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
)

MAX_SUBS_PER_SECOND = 50  # concurrency limit

def acquire_lock(user_id, timeout=5):
    key = f"grammar_sub_lock:{user_id}"
    return redis.set(key, "1", nx=True, ex=timeout)

def release_lock(user_id):
    key = f"grammar_sub_lock:{user_id}"
    redis.delete(key)

def rate_limit():
    now_sec = int(timezone.now().timestamp())
    key = f"grammar_sub_rate:{now_sec}"
    count = redis.incr(key)
    redis.expire(key, 2)
    return count <= MAX_SUBS_PER_SECOND

# -------------------------
# Initiate subscription payment
# -------------------------
def grammar_start_subscription(request):
    if not request.user.is_authenticated:
        return HttpResponse("""
            <script>
                alert("⚠ Please sign up or log in before subscribing.");
                window.history.back();
            </script>
        """)

    if not rate_limit():
        return JsonResponse({"error": "Too many subscription attempts. Try again in a second."}, status=429)

    # Fetch or create profile
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Currency and amount
    currency = request.GET.get("currency", "NGN").upper()
    if currency not in ["NGN", "USD"]:
        return JsonResponse({"error": "Invalid currency"}, status=400)

    amount = 4000 if currency == "NGN" else 4
    tx_ref = f"grammar-{uuid.uuid4().hex[:10]}"

    user_profile.flutterwave_tx_ref = tx_ref
    user_profile.save()

    payment_options = (
        "card,banktransfer,ussd,ngn,ussd_qr,eNaira"
        if currency == "NGN"
        else "card,applepay,googlepay,banktransfer"
    )

    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": currency,
        "redirect_url": request.build_absolute_uri("/grammar-verify-subscription/"),
        "payment_options": payment_options,
        "customer": {
            "email": request.user.email or f"user{request.user.id}@example.com",
            "name": request.user.username
        },
        "customizations": {
            "title": "Grammar Pro Subscription",
            "description": "Unlock 50 checks/day and 5,000 words"
        }
    }

    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}

    try:
        res = requests.post("https://api.flutterwave.com/v3/payments", json=payload, headers=headers, timeout=15)
        res_data = res.json()
        logger.info(f"Flutterwave init payment: {res_data}")
    except requests.RequestException as e:
        logger.exception("Flutterwave request failed (grammar)")
        return JsonResponse({"error": f"Failed to initiate payment: {str(e)}"}, status=500)

    if res_data.get("status") == "success" and "link" in res_data.get("data", {}):
        return redirect(res_data["data"]["link"])

    return JsonResponse({"error": "Failed to initiate payment"}, status=400)

# -------------------------
# Verify payment & handle subscription
# -------------------------
@login_required
def grammar_verify_subscription(request):
    tx_ref = request.GET.get("tx_ref")
    if not tx_ref:
        return redirect("/grammar-checker/")

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Ensure tx_ref matches user's last initiated payment
    if tx_ref != user_profile.flutterwave_tx_ref:
        logger.warning(f"TX_REF mismatch for user {request.user.id}: {tx_ref} vs {user_profile.flutterwave_tx_ref}")
        return redirect("/grammar-checker/?subscribed=0")

    # Acquire lock
    if not acquire_lock(user_profile.user.id):
        return JsonResponse({"error": "Another subscription update in progress. Try again."}, status=429)

    try:
        # Verify payment
        verify_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
        headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
        res = requests.get(verify_url, headers=headers, timeout=15)
        res_data = res.json()

        if res_data.get("status") != "success":
            logger.error(f"Payment verification failed: {res_data}")
            return redirect("/grammar-checker/?subscribed=0")

        payment_status = res_data["data"].get("status", "").lower()
        payment_currency = res_data["data"].get("currency")
        payment_amount = float(res_data["data"].get("amount", 0))

        expected_amount = 4000 if payment_currency == "NGN" else 4
        if payment_amount != expected_amount:
            logger.error(f"Payment amount mismatch: expected {expected_amount}, got {payment_amount}")
            refund_payment(tx_ref, payment_amount, payment_currency)
            return redirect("/grammar-checker/?subscribed=0")

        if payment_status == "successful":
            with transaction.atomic():
                user_profile.is_subscribed = True
                user_profile.subscription_start = timezone.now()
                user_profile.subscription_end = timezone.now() + timedelta(days=30)
                user_profile.flutterwave_tx_ref = tx_ref
                user_profile.save()
            return redirect("/grammar-checker/?subscribed=1")

        else:
            # Payment failed, auto-refund if captured
            logger.warning(f"Payment failed for user {request.user.id}: {res_data['data']}")
            refund_payment(tx_ref, payment_amount, payment_currency)
            return redirect("/grammar-checker/?subscribed=0")

    finally:
        release_lock(user_profile.user.id)

# -------------------------
# Refund helper
# -------------------------
def refund_payment(tx_ref, amount, currency):
    """
    Calls Flutterwave refund API for failed or mismatched payments.
    """
    refund_url = "https://api.flutterwave.com/v3/transactions/refund"
    payload = {
        "tx_ref": tx_ref,
        "amount": amount,
        "currency": currency,
        "narration": "Grammar subscription failed, automatic refund"
    }
    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    try:
        res = requests.post(refund_url, json=payload, headers=headers, timeout=15)
        res_data = res.json()
        logger.info(f"Refund requested for {tx_ref}: {res_data}")
    except requests.RequestException as e:
        logger.exception(f"Refund failed for {tx_ref}: {str(e)}")


@login_required
def grammar_subscription_status(request):
    """
    Returns current user's subscription status as JSON.
    """
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    return JsonResponse({
        "is_subscribed": user_profile.is_subscribed,
        "subscription_start": user_profile.subscription_start,
        "subscription_end": user_profile.subscription_end,
        "remaining_days": (user_profile.subscription_end - timezone.now()).days if user_profile.subscription_end else 0
    })










    
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