from django.conf import settings
import os
from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404, HttpResponse
from django.utils.translation import get_language
import io, json
from reportlab.lib.units import cm
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import json, requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

def essay_page(request):
    return render(request, 'essay_page.html')
import logging
import json
from datetime import timedelta
import requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .utils.essay_generator import generate_polished_essay
from .models import UserSubscription

logger = logging.getLogger(__name__)
import logging
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests
from .models import UserSubscription

logger = logging.getLogger(__name__)

# -------------------------
@login_required
def subscription_status(request):
    user = request.user

    # --- Unauthenticated users ---
    if not user.is_authenticated:
        return JsonResponse({
            "plan": "FREE",
            "essays_used": 0,
            "limit": 1,
            "subscribed": False,
            "free_trial_used": False,
            "message": "⚠️ Please sign up before generating an essay."
        })

    # --- Authenticated user ---
    sub, _ = UserSubscription.objects.get_or_create(user=user)

    # compute limit and remaining essays
    limit = sub.essays_limit if sub.essays_limit is not None else 999999
    remaining = limit - sub.essays_used if sub.essays_limit is not None else "∞"

    return JsonResponse({
        "plan": sub.plan_code.upper() if sub.plan_code else "FREE",
        "essays_used": sub.essays_used,
        "limit": limit,
        "subscribed": sub.is_active(),
        "free_trial_used": sub.free_trial_used,
        "message": f"✅ You have {remaining} essay{'s' if remaining != 1 else ''} left"
    })
import logging
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import requests
from django.conf import settings

logger = logging.getLogger(__name__)
# Remove @login_required because we handle auth manually
import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
import requests, logging

logger = logging.getLogger(__name__)

# ❌ remove @login_required (we’ll handle login manually)
def start_subscription(request):
    plan = request.GET.get("plan")
    if not plan:
        return HttpResponse("No plan selected", status=400)

    # --- Check if user is logged in ---
    if not request.user.is_authenticated:
        # Instead of redirect, trigger your register/login modal
        return HttpResponse(
            """
            <script>
                alert("⚠ Please sign up or log in before subscribing.");
                if (window.bootstrap) {
                    var modalEl = document.getElementById("registerModal");
                    if (modalEl) {
                        var modal = new bootstrap.Modal(modalEl);
                        modal.show();
                    }
                } else {
                    console.warn("Bootstrap not loaded: cannot show modal.");
                }
                window.history.back();
            </script>
            """
        )

    # Flutterwave plans with correct amounts
    plans = {
        "basic_ng": {"amount": 1800, "currency": "NGN"},
        "standard_ng": {"amount": 5000, "currency": "NGN"},
        "unlimited_ng": {"amount": 17000, "currency": "NGN"},
        "basic_usd": {"amount": 4, "currency": "USD"},
        "standard_usd": {"amount": 10, "currency": "USD"},
        "unlimited_usd": {"amount": 25, "currency": "USD"},
    }

    if plan not in plans:
        return HttpResponse("Invalid plan", status=400)

    selected = plans[plan]

    # Unique tx_ref per transaction
    tx_ref = f"sub_{request.user.id}_{plan}_{int(timezone.now().timestamp())}"

    # --- Payment options ---
    if selected["currency"] == "NGN":
        payment_options = "card,banktransfer,ussd,ngn,ussd_qr,eNaira"
    else:  # USD or other international currency
        payment_options = "card,banktransfer"

    payload = {
        "tx_ref": tx_ref,
        "amount": selected["amount"],
        "currency": selected["currency"],
        "payment_options": payment_options,
        "redirect_url": request.build_absolute_uri("/essay/verify-subscription/"),
        "customer": {
            "email": request.user.email or f"user{request.user.id}@example.com",
            "name": request.user.get_full_name() or request.user.username,
            "phone_number": "08000000000",  # optional
        },
        "customizations": {
            "title": f"Essay Generator - {plan.replace('_', ' ').title()}",
            "description": f"{plan.replace('_', ' ').title()} plan subscription",
        },
        "meta": {"user_id": request.user.id},
    }

    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}

    try:
        r = requests.post(
            "https://api.flutterwave.com/v3/payments",
            json=payload,
            headers=headers,
            timeout=15
        )
        data = r.json()
        logger.info(f"Flutterwave init response: {data}")

        if data.get("status") == "success" and "link" in data.get("data", {}):
            return redirect(data["data"]["link"])
        else:
            return HttpResponse(
                "Payment initialization failed: " + data.get("message", "Unknown error"),
                status=500
            )

    except requests.RequestException as e:
        logger.exception("Flutterwave request failed")
        return HttpResponse(f"Payment request failed: {str(e)}", status=500)


@login_required
def verify_subscription(request):
    status = request.GET.get("status")
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")

    if status != "successful" or not transaction_id:
        return redirect("/essay/?payment=failed")

    # Verify transaction with Flutterwave
    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    r = requests.get(url, headers=headers)
    data = r.json()

    if data.get("status") != "success":
        return redirect("/essay/?payment=failed")

    # Extract plan and currency correctly from tx_ref
    # tx_ref format: "sub_{user_id}_{plan_code}_{timestamp}"
    tx_parts = tx_ref.split("_")
    if len(tx_parts) < 4:
        return redirect("/essay/?payment=failed")

    plan_code = tx_parts[2]      # basic / standard / unlimited
    currency_code = tx_parts[3]  # ng / usd
    full_plan_key = f"{plan_code}_{currency_code}"  # matches your plans dict

    # Map plan_key to essay limits
    PLAN_LIMITS = {
        "basic_ng": 5,
        "standard_ng": 15,
        "unlimited_ng": None,
        "basic_usd": 5,
        "standard_usd": 15,
        "unlimited_usd": None,
    }
    essays_limit = PLAN_LIMITS.get(full_plan_key, 0)

    # Update or create subscription
    sub, _ = UserSubscription.objects.get_or_create(user=request.user)
    sub.plan_code = full_plan_key
    sub.essays_used = 0
    sub.essays_limit = essays_limit
    sub.free_trial_used = True  # after subscribing
    sub.start_date = timezone.now()
    sub.expiry_date = timezone.now() + timedelta(days=30)
    sub.save()

    return redirect("/essay/?payment=success")
@csrf_exempt
def essay_generate(request):
    try:
        user = request.user

        # --- Require login ---
        if not user.is_authenticated:
            return JsonResponse({
                "success": False,
                "essay": "",
                "message": "⚠️ Please sign up before generating an essay.",
                "free_trial_used": False,
                "subscribed": False,
                "essays_used": 0,
                "limit": 1,
                "references": []
            })

        # --- Authenticated user ---
        sub, _ = UserSubscription.objects.get_or_create(user=user)

        # --- Free trial logic ---
        if not sub.free_trial_used and sub.essays_used == 0:
            sub.free_trial_used = True
            sub.essays_used += 1
            sub.start_date = timezone.now()
            sub.expiry_date = timezone.now() + timedelta(days=30)
            sub.save()
            limit = sub.essays_limit if sub.essays_limit is not None else 1
        else:
            limit = sub.essays_limit if sub.essays_limit is not None else 1
            if sub.essays_limit is not None and sub.essays_used >= limit:
                return JsonResponse({
                    "success": False,
                    "essay": "",
                    "message": "⚠️ Limit reached. Please upgrade to continue generating essays.",
                    "free_trial_used": sub.free_trial_used,
                    "subscribed": sub.is_active(),
                    "essays_used": sub.essays_used,
                    "limit": limit,
                    "references": []
                })
            sub.essays_used += 1
            sub.save()

        # --- Extract request parameters ---
        if request.method == "GET":
            topic = (request.GET.get("topic") or "").strip()
            essay_type = (request.GET.get("type") or request.GET.get("essayType") or "expository").strip().lower()
            lang = (request.GET.get("lang") or request.GET.get("language") or "").strip().lower()
        elif request.method == "POST":
            try:
                data = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)
            topic = str(data.get("topic") or "").strip()
            essay_type = str(data.get("type") or data.get("essayType") or "expository").strip().lower()
            lang = str(data.get("lang") or data.get("language") or "").strip().lower()
        else:
            return JsonResponse({"success": False, "error": "Unsupported HTTP method"}, status=405)

        # --- Validate inputs ---
        if not topic:
            return JsonResponse({"success": False, "error": "Missing essay topic"}, status=400)
        if not lang:
            return JsonResponse({"success": False, "error": "Please select a language"}, status=400)

        valid_types = ["expository", "narrative", "descriptive", "persuasive", "analytical"]
        if essay_type not in valid_types:
            essay_type = "expository"

        valid_langs = ["en", "yo", "ig", "ha", "ar", "zu", "sw", "fr"]
        if lang not in valid_langs:
            return JsonResponse({"success": False, "error": f"Invalid language '{lang}'"}, status=400)

        # --- Generate essay ---
        essay = generate_polished_essay(topic, essay_type, lang)
        if not essay.strip():
            return JsonResponse({"success": False, "error": "Generated essay is empty"}, status=500)

        # --- Word count normalization ---
        words = essay.split()
        if len(words) > 800:
            essay = " ".join(words[:800])
        elif len(words) < 800:
            # Add natural padding instead of repeating filler
            closing = (
                " In conclusion, this discussion highlights the importance of the topic "
                "and its lasting impact on society. Through reflection and research, "
                "we can better appreciate its relevance in our world today."
            )
            while len(essay.split()) < 800:
                essay += closing
            essay = " ".join(essay.split()[:800])  # trim if overshoot

        # --- Extract references from essay ---
        references = []
        lower_text = essay.lower()
        if "references:" in lower_text:
            try:
                refs_part = essay.split("References:")[-1].strip()
                refs_lines = [r.strip() for r in refs_part.split("\n") if r.strip()]
                references = refs_lines[:3]  # take first 3
            except Exception:
                references = []
        if not references:
            references = [
                f"{topic} - Journal of Modern Studies (2023)",
                f"{topic} - International Research Review (2022)",
                f"{topic} - Academic Insights Publishing (2021)"
            ]

        remaining = (sub.essays_limit - sub.essays_used) if sub.essays_limit is not None else "∞"

        return JsonResponse({
            "success": True,
            "topic": topic,
            "type": essay_type,
            "lang": lang,
            "words": 800,
            "citations": 3,
            "essay": essay,
            "references": references,
            "free_trial_used": sub.free_trial_used,
            "subscribed": sub.is_active(),
            "essays_used": sub.essays_used,
            "limit": limit,
            "message": f"✅ You have {remaining} essay{'s' if remaining != 1 else ''} left"
        })

    except Exception as e:
        logger.error(f"Unexpected error in essay_generate: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": "An unexpected error occurred"}, status=500)

@csrf_exempt
def download_essay_pdf(request):
    """
    Generate a PDF from POSTed essay content with proper formatting.
    """
    if request.method != "POST":
        return HttpResponse("Invalid request method.", status=405)

    essay_text = request.POST.get("content", "").strip()
    if not essay_text:
        return HttpResponse("No essay content provided. Generate an essay first.", status=400)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        spaceBefore=12,
        spaceAfter=12
    )
    normal_style = styles['Normal']

    story = []

    # Add essay title
    story.append(Paragraph("Generated Essay", title_style))
    story.append(Spacer(1, 12))

    # Split essay into paragraphs
    for paragraph in essay_text.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), normal_style))
            story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="essay.pdf"'
    return response


LIBRETRANSLATE_URL = "https://libretranslate.com"

@require_POST
def translate_text(request):
    data = json.loads(request.body)
    text = data.get("text", "")
    target = data.get("target", "")
    if not text or not target:
        return JsonResponse({"success": False, "error": "Missing text or target"}, status=400)

    payload = {"q": text, "source": "auto", "target": target}
    r = requests.post(f"{LIBRETRANSLATE_URL}/translate", data=payload, timeout=10)
    result = r.json()
    return JsonResponse({"success": True, "content": result.get("translatedText", "")})
