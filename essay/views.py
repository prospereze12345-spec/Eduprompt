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

def essay_page(request):
    return render(request, 'essay_page.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.essay_generator import generate_polished_essay
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)

@csrf_exempt
def essay_generate(request):
    """
    Generate a human-like essay.
    Accepts JSON payload or GET parameters:
        - topic / topic (mandatory)
        - type / essayType (optional, defaults to 'expository')
        - lang / language (mandatory)
    Word count and citations are fixed in utils (800 words, 3 citations).
    """
    try:
        # --- Extract parameters ---
        if request.method == "GET":
            topic = (request.GET.get("topic") or "").strip()
            essay_type = (request.GET.get("type") or request.GET.get("essayType") or "expository").strip().lower()
            lang = (request.GET.get("lang") or request.GET.get("language") or "").strip().lower()
        elif request.method == "POST":
            try:
                data = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Invalid JSON payload"}, status=400)

            topic = str(data.get("topic") or "").strip()
            essay_type = str(data.get("type") or data.get("essayType") or "expository").strip().lower()
            lang = str(data.get("lang") or data.get("language") or "").strip().lower()
        else:
            return JsonResponse({"success": False, "error": "Unsupported HTTP method"}, status=405)

        # --- Validate inputs ---
        if not topic:
            return JsonResponse({"success": False, "error": "Missing essay topic"}, status=400)
        if not lang:
            return JsonResponse({"success": False, "error": "Please select a language"}, status=400)

        valid_types = ["expository", "narrative", "descriptive", "persuasive", "analytical"]
        if essay_type not in valid_types:
            essay_type = "expository"  # fallback

        valid_langs = ["en", "yo", "ig", "ha", "ar", "zu", "sw", "fr"]
        if lang not in valid_langs:
            return JsonResponse({"success": False, "error": f"Invalid language '{lang}'"}, status=400)

        # --- Generate essay safely ---
        try:
            essay = generate_polished_essay(topic, essay_type, lang)
        except Exception as gen_err:
            logger.error(f"Essay generation error: {gen_err}", exc_info=True)
            return JsonResponse({
                "success": False,
                "error": "Essay generation failed. Please try again later."
            }, status=500)

        if not essay.strip():
            return JsonResponse({
                "success": False,
                "error": "Generated essay is empty. Please try again."
            }, status=500)

        # --- Return essay JSON ---
        return JsonResponse({
            "success": True,
            "topic": topic,
            "type": essay_type,
            "lang": lang,
            "words": 800,      # fixed
            "citations": 3,    # fixed
            "essay": essay,
        })

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in essay_generate view: {e}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "An unexpected error occurred. Please try again."
        }, status=500)

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
