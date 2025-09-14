import json
import requests
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def note_page(request):
    """Render the note generator page"""
    return render(request, "note_page.html")



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils.note import generate_study_note

@csrf_exempt
def generate_note_view(request):
    """
    Generate student-friendly study notes.
    Expects POST with JSON: { "subject": "...", "topic": "..." }
    Always returns JSON with success status.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})

    # Parse JSON payload
    try:
        data = json.loads(request.body)
        subject = data.get("subject", "").strip()
        topic = data.get("topic", "").strip()
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid JSON payload."})

    if not subject or not topic:
        return JsonResponse({"success": False, "error": "Both subject and topic are required."})

    # Generate note
    note_text = generate_study_note(subject=subject, topic=topic, max_words=500, style="student_friendly")

    # If the note returned an error, mark success as False
    if note_text.startswith("⚠️"):
        return JsonResponse({"success": False, "error": note_text})

    # Store in session if needed for PDF
    request.session['generated_note'] = note_text

    return JsonResponse({"success": True, "note": note_text})


@csrf_exempt
def download_note_pdf(request):
    """Generate a PDF from the generated note stored in session."""
    note_text = request.session.get("generated_note", "").strip()
    if not note_text:
        return HttpResponse("Please generate a note first.", status=400)

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

    story.append(Paragraph("Generated Note", title_style))
    story.append(Spacer(1, 20))

    paragraphs = note_text.split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if para:
            if para.lower().startswith(("introduction", "examples", "classwork", "assignment", "full explanation")):
                story.append(Paragraph(para, heading_style))
            else:
                story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 10))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="note.pdf"'
    return response







