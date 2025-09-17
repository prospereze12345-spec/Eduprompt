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

from .utils.ai_solver import solve_with_zhipu


@csrf_exempt
def ai_solver(request):
    """
    GET  → Render solver page
    POST → Solve a question via Zhipu and return steps + audio (multi-language)
    """
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        question = request.POST.get("question", "").strip()
        language = request.POST.get("language", "English")  # match the utils argument
        response = {"steps": "", "audio_url": ""}

        if not question:
            response["steps"] = "⚠ Please enter a question."
            return JsonResponse(response)

        try:
            # --- Clean math/science expressions ---
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

            # --- Solve with Zhipu (in selected language) ---
            steps = solve_with_zhipu(expr, max_words=200, mode="explain", language=language)
            if not steps:
                steps = f"⚠ Could not generate a solution at this time ({language})."

            # --- Generate audio in selected language ---
            audio_filename = f"tts_{abs(hash(question + language))}.mp3"
            audio_path = os.path.join(settings.MEDIA_ROOT, audio_filename)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            try:
                tts = gTTS(text=steps, lang=language)
                tts.save(audio_path)
                response["audio_url"] = os.path.join(settings.MEDIA_URL, audio_filename)
            except Exception as tts_error:
                print("⚠ gTTS failed:", tts_error)
                response["audio_url"] = ""

            response["steps"] = steps

        except Exception as e:
            response["steps"] = f"⚠️ Error occurred: {e}"

        return JsonResponse(response)

    # GET → render page
    return render(request, "ai_solver.html")


@csrf_exempt
def solve_image_api(request):
    """
    Accepts uploaded image → OCR via OCR.Space → solve with Zhipu
    """
    if request.method == "POST":
        uploaded_file = request.FILES.get("image")
        language = request.POST.get("language", "English")  # match utils

        if not uploaded_file:
            return JsonResponse({"error": "No image uploaded."}, status=400)

        try:
            # OCR using OCR.Space
            ocr_res = requests.post(
                "https://api.ocr.space/parse/image",
                files={"file": uploaded_file},
                data={"apikey": settings.OCRSPACE_API_KEY, "language": "eng"},
                timeout=30
            )
            result = ocr_res.json()
            parsed = result.get("ParsedResults")
            if not parsed or not parsed[0].get("ParsedText"):
                return JsonResponse({"error": "OCR could not extract any text."}, status=500)
            text = parsed[0]["ParsedText"].strip()
        except Exception as e:
            return JsonResponse({"error": f"OCR API failed: {e}"}, status=500)

        # Solve with Zhipu helper in chosen language
        solution = solve_with_zhipu(text, max_words=200, mode="explain", language=language)
        if not solution:
            solution = f"⚠ Could not generate a solution at this time ({language})."

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
