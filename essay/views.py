from django.conf import settings
import os
from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404, HttpResponse
from django.utils.translation import get_language
import io,json
from reportlab.lib.units import cm
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def essay_page(request):
    return render(request, 'essay_page.html', {
        'AFRICAN_LANGUAGES': settings.AFRICAN_LANGUAGES
    })



OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")


def essay_generate(request):
    """Generates essay via OpenRouter and returns JSON."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "").strip()
        essay_type = data.get("essay_type", "expository")
        language_code = data.get("language_code", "en")
    except:
        prompt = request.POST.get("prompt", "").strip()
        essay_type = request.POST.get("essay_type", "expository")
        language_code = request.POST.get("language_code", "en")

    if not prompt:
        return JsonResponse({"success": False, "error": "No topic provided."})

    full_prompt = f"Write a {essay_type} essay in {language_code} about: {prompt}"

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are an academic essay writer."},
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 800
        }

        r = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        result = r.json()
        essay_text = result["choices"][0]["message"]["content"].strip()

        return JsonResponse({"success": True, "content": essay_text})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})




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


