# views.py
import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .utils.quiz_generator import generate_quiz_from_text
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import requests, logging

from .models import QuizSubscription

logger = logging.getLogger(__name__)

@login_required
def quiz_status(request):
    user = request.user
    sub, _ = QuizSubscription.objects.get_or_create(
        user=user,
        defaults={"plan": "trial", "quizzes_limit": 3, "quizzes_used": 0}
    )

    if sub.quizzes_limit is None or sub.quizzes_limit >= 999999:  # ✅ handle unlimited
        limit = "Unlimited"
        remaining = "Unlimited"
    else:
        limit = sub.quizzes_limit
        remaining = max(0, limit - sub.quizzes_used)

    return JsonResponse({
        "success": True,
        "free_trial_used": (sub.plan == "trial" and remaining == 0),
        "subscribed": sub.is_active(),
        "quiz_left": remaining,
        "quizzes_used": sub.quizzes_used,
        "limit": limit
    })

@login_required
def quiz_subscription_status(request):
    user = request.user
    sub, _ = QuizSubscription.objects.get_or_create(
        user=user,
        defaults={"plan": "trial", "quizzes_limit": 3, "quizzes_used": 0}
    )

    # Detect Unlimited properly
    if sub.quizzes_limit is None or sub.quizzes_limit >= 999999999:
        limit = "Unlimited"
        remaining = "Unlimited"
    else:
        limit = int(sub.quizzes_limit)
        remaining = max(0, limit - sub.quizzes_used)

    trial_reached = (sub.plan == "trial" and remaining == 0)

    if trial_reached:
        message = "❌ Free trial reached. Upgrade to Pro to continue."
    elif remaining == "Unlimited":
        message = "✅ Unlimited plan active"
    else:
        message = f"✅ You have {remaining} quiz{'zes' if remaining != 1 else ''} left"

    return JsonResponse({
        "plan": sub.plan.upper() if sub.plan else "FREE",
        "quizzes_used": sub.quizzes_used,
        "limit": limit,                # ✅ string if unlimited
        "subscribed": sub.is_active(),
        "quiz_left": remaining,        # ✅ string if unlimited
        "expiry_date": sub.expiry_date,
        "trial_reached": trial_reached,
        "message": message,
    })

# # -------------------------
# Access Check Helper
# -------------------------
def _check_quiz_access(user):
    if not user.is_authenticated:
        return False, None, "⚠️ You must log in to access the Quiz Generator."

    sub, _ = QuizSubscription.objects.get_or_create(
        user=user,
        defaults={"plan": "trial", "quizzes_limit": 3, "quizzes_used": 0}
    )

    if not sub.is_active():
        return False, sub, "⚠️ Subscription expired. Please upgrade."

    # ✅ Trial plan
    if sub.plan == "trial":
        if sub.quizzes_used >= sub.quizzes_limit:
            return False, sub, "⚠️ Free trial used up. Please upgrade to continue."
        remaining = sub.quizzes_limit - sub.quizzes_used
        return True, sub, f"✅ Free trial active ({remaining} quizzes left)"

    # ✅ Unlimited plan
    if sub.quizzes_limit is None or sub.quizzes_limit >= 999999:
        return True, sub, "✅ Unlimited plan active (Unlimited quizzes left)"

    # ✅ Limited paid plan
    if sub.quizzes_used < sub.quizzes_limit:
        remaining = sub.quizzes_limit - sub.quizzes_used
        return True, sub, f"✅ Subscription active ({remaining} quizzes left)"

    # ✅ Limit reached
    return False, sub, "⚠️ Quiz limit reached. Please upgrade."
# -------------------------
# Start Subscription (Flutterwave Payment Init)
# -------------------------
from django.shortcuts import redirect
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import requests
import logging

logger = logging.getLogger(__name__)
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import requests, logging, time

logger = logging.getLogger(__name__)

# ❌ remove @login_required
def quiz_start_subscription(request):
    plan = request.GET.get("plan")
    if not plan:
        return HttpResponse("No plan selected", status=400)

    # --- Check if user is logged in ---
    if not request.user.is_authenticated:
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

    plans = {
        "basic_ng": {"amount": 1200, "currency": "NGN", "limit": 20},
        "standard_ng": {"amount": 2800, "currency": "NGN", "limit": 50},
        "unlimited_ng": {"amount": 7500, "currency": "NGN", "limit": None},
        "basic_usd": {"amount": 2, "currency": "USD", "limit": 20},
        "standard_usd": {"amount": 5, "currency": "USD", "limit": 50},
        "unlimited_usd": {"amount": 10, "currency": "USD", "limit": None},
    }

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
    tx_ref = f"quiz_{request.user.id}_{plan}_{int(time.time())}"

    # --- Set payment options based on currency ---
    if selected["currency"] == "NGN":
        payment_options = "card,banktransfer,ussd,ngn,ussd_qr,eNaira"
    else:  # USD / international
        payment_options = "card,applepay,googlepay,banktransfer"

    payload = {
        "tx_ref": tx_ref,
        "amount": selected["amount"],
        "currency": selected["currency"],
        "payment_options": payment_options,
        "redirect_url": request.build_absolute_uri(reverse("quiz_verify_subscription")),
        "customer": {
            "email": request.user.email or f"user{request.user.id}@example.com",
            "name": request.user.get_full_name() or request.user.username,
            "phone_number": "08000000000",
        },
        "customizations": {
            "title": f"Quiz Generator - {plan.replace('_', ' ').title()}",
            "description": f"{plan.replace('_', ' ').title()} plan subscription (Quiz Generator)",
        },
        "meta": {
            "user_id": request.user.id,
            "product": "quiz_generator",
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

        # ✅ Handle non-JSON safely
        try:
            data = r.json()
        except ValueError:
            logger.error(f"Flutterwave non-JSON response: {r.text}")
            return HttpResponse(
                f"Payment request failed (non-JSON): {r.text}",
                status=r.status_code
            )

        logger.info(f"Flutterwave init response: {data}")

        link = data.get("data", {}).get("link")
        if data.get("status") == "success" and link:
            return redirect(link)

        return HttpResponse(
            "Payment initialization failed: " + data.get("message", "Unknown error"),
            status=500,
        )

    except requests.RequestException as e:
        logger.exception("Flutterwave request failed")
        return HttpResponse(f"Payment request failed: {str(e)}", status=500)

# -------------------------
# Verify Subscription
# -------------------------
@login_required
def quiz_verify_subscription(request):
    status = request.GET.get("status")
    tx_ref = request.GET.get("tx_ref")
    transaction_id = request.GET.get("transaction_id")

    if status != "successful" or not transaction_id:
        return redirect("/quiz/?payment=failed")

    headers = {"Authorization": f"Bearer {settings.FLW_SECRET_KEY}"}
    url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"

    try:
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
    except requests.RequestException:
        return redirect("/quiz/?payment=failed")

    if data.get("status") != "success":
        return redirect("/quiz/?payment=failed")

    tx_parts = tx_ref.split("_")
    if len(tx_parts) < 3:
        return redirect("/quiz/?payment=failed")

    plan_code = tx_parts[2]
    currency_code = plan_code.split("_")[-1] if "_" in plan_code else "ng"
    full_plan_key = plan_code if "_" in plan_code else f"{plan_code}_{currency_code}"

    PLAN_LIMITS = {
        "basic_ng": 20,
        "standard_ng": 50,
        "unlimited_ng": 999999999,
        "basic_usd": 20,
        "standard_usd": 50,
        "unlimited_usd": 999999999,
    }
    quizzes_limit = PLAN_LIMITS.get(full_plan_key, 0)

    sub, _ = QuizSubscription.objects.get_or_create(user=request.user)
    sub.plan = "paid"
    sub.plan_code = full_plan_key
    sub.quizzes_used = 0
    sub.quizzes_limit = quizzes_limit
    sub.start_date = timezone.now()
    sub.expiry_date = timezone.now() + timedelta(days=30)
    sub.save()

    return redirect("/quiz/?payment=success")


def quiz_generator(request):
    """Render the quiz generator UI page."""
    return render(request, "quiz_generator.html")
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import json

def login_required_json(view_func):
    """Custom login_required that returns JSON instead of redirecting."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                "quiz": None,
                "error": "⚠️ Please sign up before you generate quiz.",
                "subscribed": False,
                "free_trial_used": False,
                "quizzes_used": 0
            }, status=200)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
@csrf_exempt
@login_required_json   # 👈 replaces @login_required safely
def generate_quiz(request):
    """API endpoint to generate quiz questions using Zhipu API with subscription checks."""
    if request.method != "POST":
        return JsonResponse({"quiz": None, "error": "Invalid request method. Use POST."}, status=405)

    try:
        # Parse request body safely
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"quiz": None, "error": "Invalid JSON body."}, status=400)

        study_text = body.get("quiz_text", "").strip()
        quiz_type = body.get("quiz_type", "mixed").lower()
        difficulty = body.get("difficulty", "medium").lower()
        language = body.get("language", "English").strip()
        max_questions = int(body.get("max_questions", 10))

        # Validate input
        if not study_text:
            return JsonResponse({"quiz": None, "error": "No study material provided."}, status=400)

        # --- Subscription / Trial Access Check ---
        allowed, sub, access_msg = _check_quiz_access(request.user)
        if not allowed:
            quiz_left = None
            if sub:
                raw_left = sub.quizzes_left()
                quiz_left = "Unlimited" if (raw_left is None or raw_left >= 999999) else raw_left

            return JsonResponse({
                "quiz": None,
                "error": access_msg,
                "subscribed": sub.is_active() if sub else False,
                "quiz_left": quiz_left if sub else 0,
                "free_trial_used": True,
                "quizzes_used": sub.quizzes_used if sub else 0
            }, status=200)

        # --- Generate Quiz using util ---
        result = generate_quiz_from_text(
            study_text=study_text,
            quiz_type=quiz_type,
            difficulty=difficulty,
            language=language,
            max_questions=max_questions
        )

        if result.startswith("⚠️"):
            return JsonResponse({"quiz": None, "error": result}, status=200)

        # --- Deduct 1 quiz attempt ---
        if sub:
            sub.use_quiz()

        # Success
        raw_left = sub.quizzes_left() if sub else 0
        quiz_left = "Unlimited" if (raw_left is None or raw_left >= 999999) else raw_left

        return JsonResponse({
            "quiz": result,
            "error": None,
            "subscribed": sub.is_active(),
            "quiz_left": quiz_left,   # ✅ shows "Unlimited" instead of 999999
            "quizzes_used": sub.quizzes_used
        }, status=200)

    except Exception as e:
        return JsonResponse({"quiz": None, "error": f"Server error: {e}"}, status=500)
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

# ✅ Import directly from utils (not utils.quiz_generator)
from .utils.quiz_generator import generate_quiz_from_text, _check_quiz_access


@csrf_exempt
@login_required
def upload_and_generate_quiz(request):
    """
    Accepts file upload, extracts text, and generates quiz questions.
    """
    if request.method != "POST" or not request.FILES.get("file"):
        return JsonResponse({"quiz": None, "error": "Upload a file with POST."}, status=400)

    try:
        uploaded_file = request.FILES["file"]
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        # --- Extract text ---
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == ".docx":
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".pdf":
            from pypdf import PdfReader   # ✅ use pypdf instead of PyPDF2
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])

        if not text.strip():
            return JsonResponse({"quiz": None, "error": "File is empty or unsupported."}, status=400)

        # --- Subscription check ---
        allowed, sub, access_msg = _check_quiz_access(request.user)
        if not allowed:
            quiz_left = None
            if sub:
                raw_left = sub.quizzes_left()
                quiz_left = "Unlimited" if (raw_left is None or raw_left >= 999999) else raw_left
            return JsonResponse({
                "quiz": None,
                "error": access_msg,
                "subscribed": sub.is_active() if sub else False,
                "quiz_left": quiz_left if sub else 0,
                "free_trial_used": True,
                "quizzes_used": sub.quizzes_used if sub else 0
            }, status=200)

        # --- Generate Quiz ---
        result = generate_quiz_from_text(
            study_text=text,
            quiz_type="mixed",
            difficulty="medium",
            language="English",
            max_questions=10
        )

        # ✅ Always normalize result to string
        if isinstance(result, list):
            result = "\n".join(map(str, result))

        # ✅ Handle error messages
        if isinstance(result, str) and result.startswith("⚠️"):
            return JsonResponse({"quiz": None, "error": result}, status=200)

        # --- Update subscription ---
        if sub:
            sub.use_quiz()

        raw_left = sub.quizzes_left() if sub else 0
        quiz_left = "Unlimited" if (raw_left is None or raw_left >= 999999) else raw_left

        return JsonResponse({
            "quiz": result,
            "error": None,
            "subscribed": sub.is_active() if sub else False,
            "quiz_left": quiz_left,
            "quizzes_used": sub.quizzes_used if sub else 0
        }, status=200)

    except Exception as e:
        return JsonResponse({"quiz": None, "error": f"Server error: {e}"}, status=500)


@csrf_exempt
def download_quiz_pdf(request):
    """Download the generated quiz as a PDF."""
    if request.method != "POST":
        return HttpResponse("Invalid request method. Use POST.", status=405)

    quiz_text = request.POST.get("quiz_text", "").strip()
    if not quiz_text:
        return HttpResponse("No quiz content provided.", status=400)

    # Clean up text
    quiz_text = quiz_text.replace("■", "")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    paragraphs = []
    for line in quiz_text.split("\n"):
        if not line.strip():
            paragraphs.append(Spacer(1, 12))
        else:
            paragraphs.append(Paragraph(line, normal_style))

    doc.build(paragraphs)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quiz.pdf"'
    return response
