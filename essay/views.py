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
import json, requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def essay_page(request):
    return render(request, 'essay_page.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.essay_generator import generate_polished_essay
import json

import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.essay_generator import generate_polished_essay

@csrf_exempt  # allows POST requests without CSRF token
def essay_generate(request):
    """
    Generate a highly human-like essay based on topic and type selected by user.
    Accepts both GET and POST requests:
        - topic: string, essay topic
        - type: string, essay type (expository, narrative, descriptive, persuasive, analytical)
    Returns JSON:
        {
            "topic": "...",
            "type": "...",
            "essay": "..."
        }
    """
    try:
        # === Extract topic and essay_type ===
        if request.method == "GET":
            topic = request.GET.get("topic", "The role of technology in education").strip()
            essay_type = request.GET.get("type", "expository").strip().lower()
        elif request.method == "POST":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON payload"}, status=400)

            topic = data.get("topic", "The role of technology in education").strip()
            essay_type = data.get("type", "expository").strip().lower()
        else:
            return JsonResponse({"error": "Unsupported HTTP method"}, status=405)

        # === Validate essay type ===
        valid_types = ["expository", "narrative", "descriptive", "persuasive", "analytical"]
        if essay_type not in valid_types:
            essay_type = "expository"

        # === Generate essay using helper ===
        essay = generate_polished_essay(topic, essay_type)

        # Ensure response is clean and human-like
        if not essay or len(essay.strip()) == 0:
            essay = "Sorry, unable to generate essay at this time. Please try again."

        # === Return JSON response ===
        return JsonResponse({
            "success": True,
            "topic": topic,
            "type": essay_type,
            "essay": essay
        })

    except Exception as e:
        # Log detailed traceback for debugging
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)


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