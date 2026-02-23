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
import json
from threading import Thread, BoundedSemaphore
from datetime import timedelta

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import UserSubscription, Essay
from .utils.essay_generator import generate_polished_essay

MAX_CONCURRENT = 20
semaphore = BoundedSemaphore(MAX_CONCURRENT)


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

        # --- Get or create user subscription ---
        sub, _ = UserSubscription.objects.get_or_create(user=user)

        # --- Free trial logic ---
        if not sub.free_trial_used and sub.essays_used == 0:
            sub.free_trial_used = True
            sub.essays_used += 1
            sub.start_date = timezone.now()
            sub.expiry_date = timezone.now() + timedelta(days=30)
            sub.save()
            limit = sub.essays_limit if sub.essays_limit else 1
        else:
            limit = sub.essays_limit if sub.essays_limit else 1
            if sub.essays_limit and sub.essays_used >= limit:
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

        # --- Extract parameters ---
        if request.method == "GET":
            topic = (request.GET.get("topic") or "").strip()
            essay_type = (request.GET.get("type") or request.GET.get("essayType") or "expository").strip().lower()
            lang = (request.GET.get("lang") or request.GET.get("language") or "en").strip().lower()
        elif request.method == "POST":
            try:
                data = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)
            topic = str(data.get("topic") or "").strip()
            essay_type = str(data.get("type") or data.get("essayType") or "expository").strip().lower()
            lang = str(data.get("lang") or data.get("language") or "en").strip().lower()
        else:
            return JsonResponse({"success": False, "error": "Unsupported HTTP method"}, status=405)

        # --- Validate inputs ---
        if not topic:
            return JsonResponse({"success": False, "error": "Missing essay topic"}, status=400)
        valid_types = ["expository", "narrative", "descriptive", "persuasive", "analytical"]
        if essay_type not in valid_types:
            essay_type = "expository"
        valid_langs = ["en", "yo", "ig", "ha", "ar", "zu", "sw", "fr"]
        if lang not in valid_langs:
            return JsonResponse({"success": False, "error": f"Invalid language '{lang}'"}, status=400)

        # --- Background function for essay generation ---
        def generate_and_store():
            try:
                with semaphore:
                    essay_text = generate_polished_essay(topic, essay_type, lang)
            except Exception as e:
                print(f"Essay generation failed: {e}")
                essay_text = f"Fallback essay for '{topic}'. Please try again later."

            try:
                Essay.objects.create(
                    topic=topic,
                    essay_type=essay_type,
                    content=essay_text,
                    language_code=lang
                )
            except Exception as e:
                print(f"Failed to save essay: {e}")

        # --- Start generation in background ---
        Thread(target=generate_and_store, daemon=True).start()

        # --- Immediate response ---
        remaining = (sub.essays_limit - sub.essays_used) if sub.essays_limit else "∞"
        return JsonResponse({
            "success": True,
            "topic": topic,
            "type": essay_type,
            "lang": lang,
            "words": 0,
            "citations": 0,
            "essay": "",
            "references": [],
            "free_trial_used": sub.free_trial_used,
            "subscribed": sub.is_active(),
            "essays_used": sub.essays_used,
            "limit": limit,
            "message": "⌛ Essay is being generated in the background. Check back shortly.",
            "remaining": remaining
        })

    except Exception as e:
        print(f"Unexpected error: {e}")
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
