# utils/quiz_generator.py
import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import A4
import io
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def quiz_generator(request):
    """Render the quiz generator template."""
    return render(request, "quiz_generator.html")


@csrf_exempt
def generate_quiz(request):
    """Generate up to 10 professional quiz questions using ZHAPI."""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
        quiz_text = body.get("quiz_text", "").strip()
        quiz_type = body.get("quiz_type", "mixed").lower()
        difficulty = body.get("difficulty", "medium").lower()

        if not quiz_text:
            return JsonResponse({"error": "No study material provided."}, status=400)

        # ZHAPI endpoint
        url = "https://zhapi.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.ZHAPI_API_KEY}",
            "Content-Type": "application/json",
        }

        # Professional quiz generation prompt
        prompt = f"""
Generate up to 10 professional, exam-ready {quiz_type} quiz questions from the following study material.

Guidelines:
- Difficulty level: {difficulty}
- Ensure each question is clear, unambiguous, and relevant.
- Multiple-choice: provide 4 well-thought-out options (A, B, C, D) with one correct answer clearly marked.
- True/False: provide the statement and the correct answer.
- Short answer: provide the model solution in 1–3 sentences.
- Mix factual recall, understanding, and applied reasoning.
- Format questions in a clean numbered list for easy display.

Study Material:
\"\"\"{quiz_text}\"\"\"
"""

        payload = {
            "model": "gpt-4o-mini",  # supported ZHAPI model
            "messages": [
                {"role": "system", "content": "You are an academic quiz generator. Always produce professional, exam-standard quizzes."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 900
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        try:
            data = response.json()
        except Exception:
            return JsonResponse(
                {"error": f"Invalid response from ZHAPI: {response.text}"},
                status=response.status_code
            )

        if response.status_code == 200 and "choices" in data:
            quiz = data["choices"][0]["message"]["content"]
            return JsonResponse({"quiz": quiz})

        return JsonResponse(
            {"error": data.get("error", {}).get("message", "Unknown ZHAPI error.")},
            status=response.status_code
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def download_quiz_pdf(request):
    """Download generated quiz as PDF."""
    if request.method != "POST":
        return HttpResponse("Invalid request method. Please use POST.")

    quiz_text = request.POST.get("quiz_text", "").strip()
    if not quiz_text:
        return HttpResponse("No quiz content provided.")

    # Clean up text
    quiz_text = quiz_text.replace("■", "")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    paragraphs = []
    for line in quiz_text.split("\n"):
        if line.strip() == "":
            paragraphs.append(Spacer(1, 12))
        else:
            paragraphs.append(Paragraph(line, normal_style))

    doc.build(paragraphs)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="quiz.pdf"'
    return response
