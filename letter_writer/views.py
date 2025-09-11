import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import A4
import io
from django.http import HttpResponse
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch






def letter_writer(request):
    return render(request, "letter_writer.html")



@csrf_exempt
def generate_letter(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=405)

    try:
        # Parse JSON input
        body = json.loads(request.body.decode("utf-8"))
        letter_text = body.get("letter_text", "").strip()

        if not letter_text:
            return JsonResponse({"error": "No letter text provided."}, status=400)

        # OpenRouter API endpoint
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        # Prompt to generate a fully structured, human-tone, editable letter
        prompt = f"""
Write a professional letter in natural human tone suitable for any letter type.
The letter should have a proper header, salutation, body, and closing.
- Use placeholders like [Your Name], [Organization], [Recipient's Name], [Job Title], [Date], etc.
- Separate paragraphs clearly:
    1. Introduction / purpose
    2. Supporting details / experience
    3. Connection to organization or recipient
    4. Call-to-action / conclusion
- Keep it between 400-450 words
- Add blank lines between sections for readability
- Output should be fully editable for the user
Now draft the letter based on this input: \"\"\"{letter_text}\"\"\"
"""

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a professional letter writer."},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 700
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        try:
            data = response.json()
        except Exception:
            return JsonResponse(
                {"error": f"Invalid response from OpenRouter: {response.text}"},
                status=response.status_code
            )

        if response.status_code == 200 and "choices" in data:
            letter = data["choices"][0]["message"]["content"]
            return JsonResponse({"letter": letter})

        return JsonResponse(
            {"error": data.get("error", {}).get("message", "Unknown OpenRouter error.")},
            status=response.status_code
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




@csrf_exempt
def download_letter_pdf(request):
    if request.method != "POST":
        return HttpResponse("Invalid request method. Please use POST.")

    letter_text = request.POST.get("letter_text", "").strip()
    if not letter_text:
        return HttpResponse("No letter content provided.")

    # Remove unwanted characters like ■
    letter_text = letter_text.replace("■", "")

    # Create buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    # Split text into paragraphs
    paragraphs = []
    for line in letter_text.split("\n"):
        if line.strip() == "":
            paragraphs.append(Spacer(1, 12))  # Add space for blank lines
        else:
            paragraphs.append(Paragraph(line, normal_style))

    # Build PDF
    doc.build(paragraphs)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="letter.pdf"'
    return response
