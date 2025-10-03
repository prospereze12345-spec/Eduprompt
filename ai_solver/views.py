from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import requests
from gtts import gTTS
import os
import re
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from .utils.ai_solver import solve_with_zhipu
import os, re, json, requests, logging
from gtts import gTTS
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import AISolverSubscription

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import AISolverSubscription
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import requests, json, os, re, logging
from gtts import gTTS
from django.conf import settings

logger = logging.getLogger(__name__)

# -------------------------
# Simple Status (legacy/free trial only)
# -------------------------
@login_required
def solver_status(request):
    user = request.user
    sub, _ = AISolverSubscription.objects.get_or_create(
        user=user,
        defaults={"plan": "trial", "solver_limit": 3, "solver_used": 0}
    )

    # Handle unlimited
    if sub.solver_limit is None:
        limit = "Unlimited"
        remaining = "Unlimited"
    else:
        limit = sub.solver_limit
        remaining = max(0, limit - sub.solver_used)

    return JsonResponse({
        "success": True,
        "free_trial_used": (sub.plan == "trial" and remaining == 0),
        "subscribed": sub.is_active(),
        "solver_left": remaining,
        "solutions_used": sub.solver_used,
        "limit": limit
    })


# -------------------------
# Subscription Status (main)
# -------------------------
@login_required
def subscription_status(request):
    user = request.user
    sub, _ = AISolverSubscription.objects.get_or_create(
        user=user,
        defaults={"plan": "trial", "solver_limit": 3, "solver_used": 0}
    )

    # Normalize solver_limit → always return "Unlimited" for very high values
    if sub.solver_limit is None or sub.solver_limit >= 999999999:
        limit = "Unlimited"
        remaining = "Unlimited"
    else:
        limit = sub.solver_limit
        remaining = max(0, limit - sub.solver_used)

    # Detect free trial exhaustion
    trial_reached = (sub.plan == "trial" and remaining == 0)

    # Build status message
    if trial_reached:
        message = "❌ Free trial reached. Upgrade to Pro to continue."
    elif remaining == "Unlimited":
        message = "✅ Unlimited plan active"
    else:
        message = f"✅ You have {remaining} solve{'s' if remaining != 1 else ''} left"

    return JsonResponse({
        "plan": sub.plan.upper() if sub.plan else "FREE",
        "solves_used": sub.solver_used,
        "limit": "Unlimited" if limit == "Unlimited" else int(limit),
        "subscribed": sub.is_active(),
        "solver_left": "Unlimited" if remaining == "Unlimited" else int(remaining),
        "expiry_date": sub.expiry_date,
        "trial_reached": trial_reached,
        "message": message,
    })


# -------------------------
# Access Check Helper
# -------------------------
def _check_solver_access(user):
    # First, check if user is logged in
    if not user.is_authenticated:
        return False, None, "⚠️ You must log in to access the AI solver."

    # Get or create a subscription
    sub, _ = AISolverSubscription.objects.get_or_create(
        user=user,
        defaults={
            "plan": "trial",
            "solver_limit": 3,  # 3 questions free trial
            "solver_used": 0
        }
    )

    # Check if subscription is active
    if not sub.is_active():
        return False, sub, "⚠️ Subscription expired. Please upgrade."

    # Free trial logic
    if sub.plan == "trial":
        if sub.solver_used >= sub.solver_limit:
            return False, sub, "⚠️ Free trial used up. Please upgrade to continue."
        return True, sub, f"✅ Free trial active ({sub.solver_limit - sub.solver_used} solves left)"

    # Paid plan logic
    if sub.solver_limit is None or sub.solver_limit > 999999:  # Treat very high numbers as unlimited
        return True, sub, "✅ Unlimited plan active"

    if sub.solver_used < sub.solver_limit:
        remaining = sub.solver_limit - sub.solver_used
        return True, sub, f"✅ Subscription active ({remaining} solves left)"

    # If none of the above, limit reached
    return False, sub, "⚠️ Solve limit reached. Please upgrade."
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

    # AI Solver pricing
    plans = {
        "basic_ng": {"amount": 1500, "currency": "NGN", "limit": 20},
        "standard_ng": {"amount": 4500, "currency": "NGN", "limit": 70},
        "unlimited_ng": {"amount": 12000, "currency": "NGN", "limit": None},
        "basic_usd": {"amount": 3, "currency": "USD", "limit": 20},
        "standard_usd": {"amount": 8, "currency": "USD", "limit": 70},
        "unlimited_usd": {"amount": 20, "currency": "USD", "limit": None},
    }

    # Map frontend aliases → internal plan keys
    plan_aliases = {
        "basic_ngn": "basic_ng",
        "standard_ngn": "standard_ng",
        "unlimited_ngn": "unlimited_ng",
        "basic_usdollar": "basic_usd",
        "standard_usdollar": "standard_usd",
        "unlimited_usdollar": "unlimited_usd",
    }
    plan = plan_aliases.get(plan, plan)

    if plan not in plans:
        return HttpResponse("Invalid plan", status=400)

    selected = plans[plan]
    tx_ref = f"solver_{request.user.id}_{plan}_{int(timezone.now().timestamp())}"

    # --- Set payment options based on currency ---
    if selected["currency"] == "NGN":
        payment_options = "card,banktransfer,ussd,ngn,ussd_qr,eNaira"
    else:  # USD or other international currency
        payment_options = "card,banktransfer"

    payload = {
        "tx_ref": tx_ref,
        "amount": selected["amount"],
        "currency": selected["currency"],
        "payment_options": payment_options,  # ✅ dynamic options
        "redirect_url": request.build_absolute_uri(reverse("solver_verify_subscription")),
        "customer": {
            "email": request.user.email or f"user{request.user.id}@example.com",
            "name": request.user.get_full_name() or request.user.username,
            "phone_number": "08000000000",
        },
        "customizations": {
            "title": f"AI Solver - {plan.replace('_', ' ').title()}",
            "description": f"{plan.replace('_', ' ').title()} plan subscription (AI Solver)",
        },
        "meta": {
            "user_id": request.user.id,
            "product": "ai_solver",
            "plan_key": plan,
        },
    }

    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}

    try:
        r = requests.post(
            "https://api.flutterwave.com/v3/payments",
            json=payload,
            headers=headers,
            timeout=15,
        )
        data = r.json()
        logger.info(f"Flutterwave init response: {data}")

        link = data.get("data", {}).get("link")
        if data.get("status") == "success" and link:
            return redirect(link)
        return HttpResponse(
            "Payment initialization failed: " + data.get("message", "Unknown error"), status=500
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
        return redirect("/solver/?payment=failed")

    # Verify transaction with Flutterwave
    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
    except requests.RequestException:
        return redirect("/solver/?payment=failed")

    if data.get("status") != "success":
        return redirect("/solver/?payment=failed")

    # Extract plan from tx_ref → "solver_{user_id}_{plan_code}_{currency}_{timestamp}"
    tx_parts = tx_ref.split("_")
    if len(tx_parts) < 4:
        return redirect("/solver/?payment=failed")

    plan_code = tx_parts[2]       # e.g. basic / standard / unlimited
    currency_code = tx_parts[3]   # e.g. ng / usd
    full_plan_key = f"{plan_code}_{currency_code}"

    # Plan limits mapping (no None → store big number instead for unlimited)
    PLAN_LIMITS = {
        "basic_ng": 20,
        "standard_ng": 70,
        "unlimited_ng": 999999999,   # unlimited = very large number
        "basic_usd": 20,
        "standard_usd": 70,
        "unlimited_usd": 999999999,
    }
    solves_limit = PLAN_LIMITS.get(full_plan_key, 0)

    # Update or create subscription
    sub, _ = AISolverSubscription.objects.get_or_create(user=request.user)
    sub.plan = "paid"   # mark as paid
    sub.plan_code = full_plan_key
    sub.solver_used = 0   # reset usage on new payment
    sub.solver_limit = solves_limit
    sub.start_date = timezone.now()
    sub.expiry_date = timezone.now() + timedelta(days=30)  # 30-day cycle
    sub.save()

    return redirect("/ai-solver/?payment=success")

@csrf_exempt
def ai_solver(request):
    response = {"success": False, "solution": "", "steps": "", "audio_url": "", "question": "", "message": ""}

    # --- Only POST requests for solving ---
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":

        if not request.user.is_authenticated:
            response["message"] = "⚠️ Please sign up before you start solving."
            return JsonResponse(response, status=403)

        try:
            if request.content_type == "application/json":
                data = json.loads(request.body.decode("utf-8"))
            else:
                data = request.POST
        except Exception:
            response["message"] = "⚠ Invalid request format."
            return JsonResponse(response, status=400)

        # --- Get question from text input or image ---
        question = (data.get("question") or "").strip()
        language = data.get("lang") or data.get("language", "English")
        uploaded_file = request.FILES.get("image")

        # --- If an image is uploaded, do OCR ---
        if uploaded_file:
            try:
                ocr_res = requests.post(
                    "https://api.ocr.space/parse/image",
                    files={"file": uploaded_file},
                    data={"apikey": settings.OCRSPACE_API_KEY, "language": "eng"},
                    timeout=30
                )
                result = ocr_res.json()
                parsed = result.get("ParsedResults")
                if not parsed or not parsed[0].get("ParsedText"):
                    response["message"] = "⚠ OCR could not extract text."
                    return JsonResponse(response, status=500)
                question = parsed[0]["ParsedText"].strip()
                response["question"] = question  # populate extracted text in input box
            except Exception as e:
                response["message"] = f"OCR API failed: {e}"
                return JsonResponse(response, status=500)

        if not question:
            response["message"] = "⚠ Please enter a question or upload an image."
            return JsonResponse(response, status=400)

        # --- Subscription check ---
        allowed, sub, msg = _check_solver_access(request.user)
        if not allowed:
            response["message"] = msg
            return JsonResponse(response, status=403)

        if sub.plan == "trial":
            msg = f"🎁 Free Trial: {sub.solver_limit - sub.solver_used} solve{'s' if sub.solver_limit - sub.solver_used != 1 else ''} left"

        # --- Solve the question ---
        try:
            expr = question.replace("^", "**")
            steps = solve_with_zhipu(expr, max_words=200, mode="explain", language=language)
            if not steps:
                steps = f"⚠ Could not generate a solution at this time ({language})."

            response["steps"] = steps
            response["solution"] = steps

            # --- Generate TTS audio ---
            try:
                audio_filename = f"tts_{abs(hash(question + language))}.mp3"
                audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
                os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

                tts = gTTS(text=steps, lang="en")
                tts.save(audio_path)
                response["audio_url"] = os.path.join(settings.MEDIA_URL, audio_filename)
            except Exception as tts_error:
                logger.warning("⚠ gTTS failed: %s", tts_error)

            sub.solver_used += 1
            sub.save(update_fields=["solver_used"])

            response["success"] = True
            response["message"] = msg or "✅ Solved successfully."
        except Exception as e:
            logger.exception("Solver failed")
            response["message"] = f"⚠️ Error occurred: {e}"

        return JsonResponse(response)

    return render(request, "ai_solver.html")
@csrf_exempt
def solve_image_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    response = {"success": False, "solution": "", "question": "", "message": ""}

    # --- Check if user is authenticated ---
    if not request.user.is_authenticated:
        response["message"] = "⚠️ Please sign up before you start solving."
        return JsonResponse(response, status=403)

    # --- Parse language from request ---
    try:
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
            language = data.get("lang") or data.get("language", "en")
        else:
            data = request.POST
            language = data.get("lang") or data.get("language", "en")
    except Exception:
        language = "en"

    # --- Map frontend language to OCR.space valid codes ---
    ocr_lang_map = {
        "en": "eng",   # English
        "fr": "fre",   # French
        "ar": "ara",   # Arabic
        "sw": "swa",   # Swahili
        # Unsupported OCR languages -> fallback to English OCR
        "ig": "eng",   # Igbo
        "yo": "eng",   # Yoruba
        "ha": "eng",   # Hausa
        "zu": "eng",   # Zulu
    }
    ocr_lang = ocr_lang_map.get(language, "eng")

    # --- Check subscription / access ---
    allowed, sub, msg = _check_solver_access(request.user)
    if not allowed:
        response["message"] = msg
        return JsonResponse(response, status=403)

    # Customize free trial message
    if sub.plan == "trial":
        msg = f"🎁 Free Trial: {sub.solver_limit - sub.solver_used} solve{'s' if sub.solver_limit - sub.solver_used != 1 else ''} left"

    # --- Check uploaded image ---
    uploaded_file = request.FILES.get("image")
    if not uploaded_file:
        response["message"] = "⚠ No image uploaded."
        return JsonResponse(response, status=400)

    try:
        # --- OCR using OCR.space API ---
        ocr_res = requests.post(
            "https://api.ocr.space/parse/image",
            files={"file": uploaded_file},
            data={
                "apikey": settings.OCRSPACE_API_KEY,
                "language": ocr_lang,
                "isOverlayRequired": False
            },
            timeout=30
        )
        result = ocr_res.json()

        parsed = result.get("ParsedResults")
        if not parsed or not parsed[0].get("ParsedText"):
            err_msg = result.get("ErrorMessage") or ["⚠ could not extract text."]
            response["message"] = err_msg[0] if isinstance(err_msg, list) else str(err_msg)
            return JsonResponse(response, status=500)

        text = parsed[0]["ParsedText"].strip()
        response["question"] = text

    except Exception as e:
        response["message"] = f"OCR API failed: {e}"
        return JsonResponse(response, status=500)

    # --- Split OCR text into multiple questions ---
    questions = [q.strip() for q in text.split("\n") if q.strip()]
    solutions = []

    for idx, q in enumerate(questions[:20], start=1):  # limit to 20 questions
        try:
            sol = solve_with_zhipu(
                q,
                max_words=300,  # cap at 300 words per question
                mode="explain",
                language=language  # user-selected language
            )
            if not sol:
                sol = f"⚠ Could not generate a solution for Question {idx}."
            solutions.append(f"Q{idx}: {q}\nAnswer: {sol}\n")
        except Exception as e:
            solutions.append(f"Q{idx}: {q}\nAnswer: ❌ Error: {str(e)}\n")

    final_solution = "\n".join(solutions)

    response["solution"] = final_solution
    response["success"] = True
    response["message"] = msg or "✅ Solved successfully."

    # --- Update subscription usage ---
    sub.solver_used += 1
    sub.save(update_fields=["solver_used"])

    return JsonResponse(response)

@csrf_exempt
def download_solution_pdf(request):
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        solution = request.POST.get("solution", "").strip()

        if not solution:
            solution = "No solution available."

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        margin = 50
        y = height - margin

        # Create a text object for line wrapping
        text = p.beginText()
        text.setTextOrigin(margin, y)
        text.setFont("Helvetica", 12)

        # Title
        text.setFont("Helvetica-Bold", 16)
        text.textLine("AI Solver Solution")
        text.setFont("Helvetica", 12)
        text.textLine("")  # blank line

        # Question
        if question:
            text.setFont("Helvetica-Bold", 14)
            text.textLine("Question:")
            text.setFont("Helvetica", 12)
            for line in question.splitlines():
                max_chars = 90
                while len(line) > max_chars:
                    text.textLine(line[:max_chars])
                    line = line[max_chars:]
                text.textLine(line)
            text.textLine("")

        # Solution
        text.setFont("Helvetica-Bold", 14)
        text.textLine("Solution:")
        text.setFont("Helvetica", 12)
        for line in solution.splitlines():
            max_chars = 90
            while len(line) > max_chars:
                text.textLine(line[:max_chars])
                line = line[max_chars:]
            text.textLine(line)

        p.drawText(text)
        p.showPage()
        p.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=solution.pdf"
        })

    return HttpResponse("Invalid request method.", status=400)
