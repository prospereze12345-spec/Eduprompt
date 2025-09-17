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


def quiz_generator(request):
    """Render the quiz generator UI page."""
    return render(request, "quiz_generator.html")


@csrf_exempt
def generate_quiz(request):
    """API endpoint to generate quiz questions using Zhipu API."""
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
        language = body.get("language", "English").strip()  # 🌍 NEW
        max_questions = int(body.get("max_questions", 10))   # 🔢 NEW

        # Validate input
        if not study_text:
            return JsonResponse({"quiz": None, "error": "No study material provided."}, status=400)

        # Call quiz generator util
        result = generate_quiz_from_text(
            study_text=study_text,
            quiz_type=quiz_type,
            difficulty=difficulty,
            language=language,
            max_questions=max_questions  # ✅ pass here
        )

        if result.startswith("⚠️"):
            # API or validation error
            return JsonResponse({"quiz": None, "error": result}, status=200)

        # Success
        return JsonResponse({"quiz": result, "error": None}, status=200)

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
