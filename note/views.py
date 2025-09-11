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





OPENROUTER_KEY = getattr(settings, "OPENROUTER_KEY", "")

@csrf_exempt
def generate_note(request):
    """Generate study notes in simple, clear paragraphs with main subheadings."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})

    # Extract subject and topic from JSON or POST
    try:
        data = json.loads(request.body)
        subject = data.get("subject", "").strip()
        topic = data.get("topic", "").strip()
    except (json.JSONDecodeError, TypeError):
        subject = request.POST.get("subject", "").strip()
        topic = request.POST.get("topic", "").strip()

    if not subject or not topic:
        return JsonResponse({"success": False, "error": "Both subject and topic are required."})

    # Prompt for OpenRouter AI
    prompt = (
        f"You are an expert teacher creating high-quality, interactive study notes for students. "
        f"Generate notes for the subject '{subject}' on the topic '{topic}' in clear, simple, and natural language. "
        f"Explain each concept thoroughly with examples, step-by-step reasoning, and relevant formulas. "
        f"Write as if speaking directly to a student, encouraging understanding, engagement, and curiosity.\n\n"

        f"Organize the notes using these main sections (use headings only for these sections; for subsections, use H5 headings):\n"
        f"1. Introduction: Provide a clear overview of the topic, its importance, and its context within the subject. "
        f"Include one motivating question to engage the student.\n"
        f"2. Key Definitions: Define all critical terms in simple language, with examples where needed.\n"
        f"3. Full Explanation: Explain concepts in detail, step-by-step. Include formulas, calculations, derivations, text-based diagrams, and examples. "
        f"Break complex ideas into smaller, easy-to-understand parts.\n"
        f"4. Common Mistakes: Highlight typical student errors, explain why they occur, and how to avoid them.\n"
        f"5. Tips and Tricks: Provide mnemonics, memory aids, shortcuts, or visualization techniques to remember key concepts.\n"
        f"6. Examples (H5 heading): Illustrate 2–3 key points with fully explained examples in paragraph form. Show the reasoning clearly.\n"
        f"7. Classwork (H5 heading): Provide 3 guided exercises in paragraph form, including problems, steps to solve, and explanations.\n"
        f"8. Assignment (H5 heading): Offer 3 additional practice problems in paragraph form, with hints or partial solutions.\n"
        f"9. Mini-Quiz: Include 2–3 short conceptual questions with answers provided separately for self-testing.\n"
        f"10. Discussion Prompt: Pose 1–2 open-ended questions to encourage reflection or exploration beyond the topic.\n"
        f"11. Summary: Conclude with key takeaways, formulas, and essential concepts students must remember.\n\n"

        f"Additional Requirements:\n"
        f"- Do not use bullet points, numbered lists, markdown symbols, asterisks, or slashes except for section headings.\n"
        f"- Use a natural, conversational, teacher-to-student tone with simple grammar.\n"
        f"- Ensure content is highly detailed, interactive, and easy to study from.\n"
        f"- Include reasoning, examples, and context to make learning engaging.\n"
        f"- Gradually build understanding from simple to complex.\n"
        f"- Describe diagrams or visualizations in words so students can imagine or draw them.\n"
        f"- Make exercises and assignments realistic and relevant to the topic.\n"
        f"- Mini-quiz and discussion prompts are optional but highly encouraged for active learning."
    )

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a professional study assistant and educator."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return JsonResponse({
                "success": False,
                "error": f"API returned {response.status_code}: {response.text}"
            })

        result = response.json()
        note_text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Clean up unwanted characters
        note_text = note_text.replace("*", "").replace("/", "")

        if not note_text:
            return JsonResponse({"success": False, "error": "Failed to generate note."})

        # Store in session for PDF download
        request.session['generated_note'] = note_text

        return JsonResponse({"success": True, "note": note_text})

    except requests.exceptions.RequestException as e:
        return JsonResponse({"success": False, "error": f"API request failed: {str(e)}"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Unexpected error: {str(e)}"})




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







