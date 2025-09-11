from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import requests
from gtts import gTTS
import os
from django.conf import settings
import re
import os
import re
import requests
from gtts import gTTS
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

# ----------------------------
# OpenRouter solver
# ----------------------------
def solve_with_openrouter(question, max_tokens=200):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional tutor. Provide concise 3-5 step solutions. "
                        "Plain text only, no markdown or special symbols."
                    ),
                },
                {"role": "user", "content": question},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.5,
        }

        res = requests.post(url, json=payload, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return answer or None

    except Exception as e:
        print("⚠ OpenRouter failed:", e)
        return None

# ----------------------------
# Main Django view (matches URLs)
# ----------------------------
@csrf_exempt
def ai_solver(request):
    """
    POST: solves a user question via OpenRouter and returns steps + audio
    GET: renders the ai_solver page
    """
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        question = request.POST.get("question", "").strip()
        user_id = request.POST.get("user_id", "guest")  # simple user tracking
        response = {"steps": "", "audio_url": ""}

        if not question:
            response["steps"] = "⚠ Please enter a question."
            return JsonResponse(response)

        # Rate limit: 2 requests/day per user
        cache_key = f"ai_solver_requests:{user_id}"
        request_count = cache.get(cache_key, 0)
        if request_count >= 2:
            response["steps"] = "⚠ Daily limit reached. Try again tomorrow."
            return JsonResponse(response)
        cache.set(cache_key, request_count + 1, timeout=86400)  # 24h

        try:
            # Clean math expressions
            expr = question.replace("^", "**")
            expr = re.sub(r"∫", "integrate", expr)
            expr = re.sub(r"d/dx", "derivative(", expr, flags=re.I)
            expr = re.sub(r"log₂\((.*?)\)", r"log(\1,2)", expr)
            expr = re.sub(r"log₁₀\((.*?)\)", r"log(\1,10)", expr)
            expr = re.sub(r"[₀-₉⁰-⁹]", "", expr)
            expr = re.sub(r"(Evaluate|Compute|Calculate|from.*to.*|dx)", "", expr, flags=re.I)
            expr = expr.strip()
            if "=" in expr:
                expr = f"solve {expr}"

            # Solve with OpenRouter
            steps = solve_with_openrouter(expr)
            if not steps:
                steps = "⚠ Could not generate a solution at this time."

            # Generate audio
            audio_filename = f"tts_{abs(hash(question))}.mp3"
            audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            try:
                tts = gTTS(text=steps, lang="en")
                tts.save(audio_path)
                response["audio_url"] = os.path.join(settings.MEDIA_URL, audio_filename)
            except Exception as e:
                print("⚠ gTTS failed:", e)
                response["audio_url"] = ""

            response["steps"] = steps

        except Exception as e:
            response["steps"] = f"⚠️ Error: {e}"

        return JsonResponse(response)

    # GET request → render page
    return render(request, "ai_solver.html")


# ----------------------------
# Image OCR + Solve endpoint
# ----------------------------
@csrf_exempt
def solve_image_api(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("image")
        if not uploaded_file:
            return JsonResponse({"error": "No image uploaded."}, status=400)

        try:
            # Send image to OCR.Space API
            response = requests.post(
                "https://api.ocr.space/parse/image",
                files={"file": uploaded_file},
                data={"apikey": settings.OCRSPACE_API_KEY, "language": "eng"}
            )
            result = response.json()
            text = result['ParsedResults'][0]['ParsedText'].strip()
        except Exception as e:
            return JsonResponse({"error": f"OCR API failed: {e}"}, status=500)

        # Solve extracted text with OpenRouter
        solution = solve_with_openrouter(text)
        if not solution:
            solution = "⚠ Could not generate a solution at this time."

        return JsonResponse({
            "question": text,
            "solution": solution
        })

    return JsonResponse({"error": "Invalid request."}, status=400)

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
        line_height = 14

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
                text.textLine(line)
            text.textLine("")  # blank line

        # Solution
        text.setFont("Helvetica-Bold", 14)
        text.textLine("Solution:")
        text.setFont("Helvetica", 12)
        for line in solution.splitlines():
            # If line is too long, wrap it manually
            max_chars = 90  # adjust as needed
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
