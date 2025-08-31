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

# --- Helper function ---
def solve_with_openrouter(question, max_tokens=300):
    """Use OpenRouter GPT for step-by-step solutions safely with free-tier limits."""
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"}

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional tutor. "
                        "Explain solutions step by step in clear, simple paragraphs. "
                        "Format like:\n"
                        "Step 1: Explain the first step.\n"
                        "Step 2: Explain the next step.\n"
                        "Continue until complete. "
                        "Do NOT use #, *, or markdown formatting. Plain text only."
                    ),
                },
                {"role": "user", "content": question},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        res = requests.post(url, json=payload, headers=headers, timeout=20)
        res_json = res.json()

        if res.status_code == 402:
            print("⚠️ OpenRouter error: Free credits exceeded or request too large.")
            return "⚠️ OpenRouter free credits exceeded. Reduce question size or upgrade plan."

        if "error" in res_json:
            print("⚠️ OpenRouter error:", res_json["error"])
            return None

        answer = res_json.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not answer:
            return None

        # Ensure each step starts on a new line
        organized_answer = re.sub(r"(Step \d+:)", r"\n\1", answer).strip()
        return organized_answer

    except Exception as e:
        print("⚠️ OpenRouter exception:", e)
        return None

# --- Main Django View ---
def ai_solver(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        question = request.POST.get("question", "").strip()
        response = {"steps": "", "audio_url": ""}

        if not question:
            response["steps"] = "Please enter a question."
            return JsonResponse(response)

        try:
            # --- Clean math expressions ---
            expr = question
            expr = expr.replace("^", "**")
            expr = re.sub(r"∫", "integrate", expr)
            expr = re.sub(r"d/dx", "derivative(", expr, flags=re.I)
            expr = re.sub(r"log₂\((.*?)\)", r"log(\1,2)", expr)
            expr = re.sub(r"log₁₀\((.*?)\)", r"log(\1,10)", expr)
            expr = re.sub(r"[₀-₉⁰-⁹]", "", expr)
            expr = re.sub(r"(Evaluate|Compute|Calculate|from.*to.*|dx)", "", expr, flags=re.I)
            expr = expr.strip()
            if "=" in expr:
                expr = f"solve {expr}"

            # --- Solve with OpenRouter ---
            steps = solve_with_openrouter(expr, max_tokens=300)
            if not steps:
                steps = "⚠️ Sorry, no detailed solution could be generated at the moment."

            # --- Generate Audio ---
            audio_filename = "solution_ajax.mp3"
            audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            tts = gTTS(text=steps, lang="en")
            tts.save(audio_path)

            response["steps"] = steps
            response["audio_url"] = os.path.join(settings.MEDIA_URL, audio_filename)

        except Exception as e:
            response["steps"] = f"⚠️ Error: {e}"

        return JsonResponse(response)

    # GET request
    return render(request, "ai_solver.html", {
        "AFRICAN_LANGUAGES": getattr(settings, "AFRICAN_LANGUAGES", []),
    })

    
@csrf_exempt
def solve_image_api(request):
    """
    Accepts an uploaded image, extracts text using OCR.Space API, 
    and solves the extracted question with OpenRouter AI.
    """
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
