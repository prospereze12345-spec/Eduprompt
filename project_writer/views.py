
import json
import requests
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.http import HttpResponse
from docx import Document
from io import BytesIO




PROJECT_SECTIONS = [
    ("Title Page", "Include project title, student or organization name, date, and institution."),
    ("Abstract", "Summarize objectives, methodology, results, and recommendations in clear, structured paragraphs."),
    ("Acknowledgements", "Optional paragraph recognizing support from mentors, peers, or institutions."),
    ("Introduction", "Provide background, importance, problem statement, and objectives in readable paragraphs."),
    ("Literature Review / Related Work", "Discuss previous studies, existing solutions, challenges, and gaps with examples."),
    ("Methodology", "Describe research design, data collection, tools, software, and procedures in multiple paragraphs."),
    ("Results / Findings", "Present outcomes, observations, and relevant data with examples."),
    ("Discussion", "Interpret results, explain implications, limitations, and significance."),
    ("Conclusion", "Summarize findings and provide recommendations."),
    ("References / Bibliography", "List references relevant to the project in proper format."),
    ("Appendices", "Include supporting data, diagrams, tables, or additional material."),
    ("Future Work / Recommendations", "Suggest improvements or next steps with bullet points or paragraphs."),
    ("Summary of Key Insights", "Highlight major takeaways in a concise paragraph.")
]

def generate_openrouter_project(prompt, model=None, target_words=5000):
    """
    Generate a complete, structured, and student-friendly project/report section by section using OpenRouter API.
    Each section will have:
    - HTML <h1> heading for the section title
    - Structured paragraphs
    - Smooth transitions and examples
    - Professional, human-like writing style
    """
    model = model or getattr(settings, "OPENROUTER_DEFAULT_MODEL", "gpt-3.5-turbo")
    temperature = getattr(settings, "TEMPERATURE", 0.7)
    api_key = getattr(settings, "OPENROUTER_API_KEY", "")

    if not api_key:
        return "⚠️ OpenRouter API key is missing in settings."

    # Allocate approximate words per section
    section_word_map = {
        section[0]: max(int(target_words / len(PROJECT_SECTIONS)), 400)
        for section in PROJECT_SECTIONS
    }

    final_project = ""
    for section_name, section_desc in PROJECT_SECTIONS:
        max_tokens = section_word_map[section_name] * 2  # rough token conversion

        section_prompt = f"""
        Generate the "{section_name}" section for a professional project/report based on this idea:
        "{prompt}"

        Instructions:
        - {section_desc}
        - Write in multiple well-structured paragraphs with smooth transitions.
        - Use examples and explanations where appropriate.
        - Format the section for readability using HTML:
            <h1>{section_name}</h1>
            Paragraphs should be clear, readable, and student-friendly.
        - Use a human tone and avoid robotic phrasing.
        - Approximate word count: {section_word_map[section_name]} words.
        """

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": section_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/completions",
                headers=headers,
                json=payload,
                timeout=150  # increased timeout for large outputs
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("choices", [{}])[0].get("text", f"⚠️ No text returned for {section_name}.")

            # Organize with HTML heading for each section
            final_project += f"<h1>{section_name}</h1>\n{text.strip()}\n\n"
        except Exception as e:
            print(f"OpenRouter API error ({section_name}):", e)
            final_project += f"<h1>{section_name}</h1>\n⚠️ Could not generate this section.\n\n"

    return final_project.strip()





@csrf_exempt
def generate_project(request):
    """
    Endpoint to generate a student or organizational project.
    Stores generated content in session for later download as PDF/DOCX.
    Expects POST JSON:
    {
        "question": "<project idea>",
        "length": "short" | "medium" | "long"   # optional, defaults to medium
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    question = data.get("question", "").strip()
    if not question:
        return JsonResponse({"error": "No project idea provided."}, status=400)

    # Determine project length
    length = str(data.get("length", "medium")).lower()
    if length not in ["short", "medium", "long"]:
        length = "medium"

    length_to_words = {"short": 2000, "medium": 5000, "long": 8000}
    target_words = length_to_words.get(length, 5000)

    try:
        # Call your AI function
        answer = generate_openrouter_project(question, target_words=target_words)
    except Exception as e:
        return JsonResponse({"error": f"Project generation failed: {str(e)}"}, status=500)

    # ✅ Store in session for later download
    request.session["generated_project"] = answer
    request.session["project_length"] = length
    request.session["project_words"] = target_words

    return JsonResponse({
        "answer": answer,
        "length": length,
        "target_words": target_words,
        "message": "Project generated and stored for download."
    })






def project_writer(request):
    """
    Renders the project writer page.
    """
    return render(request, "project_writer.html")








@csrf_exempt
def download_project_pdf(request):
    """
    Generate a PDF from session-stored project sections with proper formatting.
    """
    sections = request.session.get("project_sections", [])
    if not sections:
        return HttpResponse("No project sections found in session. Generate a project first.", status=400)

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

    for idx, section in enumerate(sections):
        title = section.get("title", "Section")
        content = section.get("content", "")

        # Add page break before main sections except first
        if idx > 0 and title.lower() not in ["title page", "abstract"]:
            story.append(PageBreak())

        # Add section heading
        if title.lower() == "title page":
            story.append(Paragraph(title, title_style))
        else:
            story.append(Paragraph(title, heading_style))

        # Add content paragraphs
        for line in content.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), normal_style))
                story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="project.pdf"'
    return response





