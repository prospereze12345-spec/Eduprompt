from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt



# Create your views here.
def index(request):
    return render(request, 'index.html')


def contact(request):
    return render(request, 'contact.html')


def about(request):
    return render(request, 'about.html')


def Terms_and_Condition(request):
    return render(request, 'Terms_and_Condition.html' )


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def website(request):
    return render(request, 'website.html')
from django.core.mail import send_mail
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# -----------------------------
# Project request form
# -----------------------------
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        # Support both JSON and form-encoded POST
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST

        full_name = data.get("fullName")
        email = data.get("email")
        phone = data.get("phone")
        development_type = data.get("developmentType")
        website_type = data.get("websiteType")
        client_location = data.get("clientLocation")
        timeline = data.get("timeline")
        message = data.get("message")
        contact_method = data.get("contactMethod")

        subject = f"New Project Request from {full_name}"
        body = f"""
Name: {full_name}
Email: {email}
Phone: {phone}
Development Type: {development_type}
Website Type: {website_type}
Location: {client_location}
Timeline: {timeline}
Contact Method: {contact_method}

Message:
{message}
        """

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "Message sent successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})


# -----------------------------
# Flyer design page
# -----------------------------
def flyer_design(request):
    return render(request, "flyer_design.html")


# -----------------------------
# Flyer design request form (AJAX)
# -----------------------------
@csrf_exempt
def flyer_request(request):
    if request.method == "POST":
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST

        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        details = data.get("details")
        budget = data.get("budget", "")

        message = f"""
You have received a new flyer design request:

Name: {name}
Email: {email}
Subject: {subject}
Details: {details}
Budget: {budget}
        """

        try:
            send_mail(
                subject=f"New Flyer Design Request: {subject}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "Flyer request sent!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"})


# -----------------------------
# Contact form AJAX
# -----------------------------
@csrf_exempt
def contact_form(request):
    if request.method == "POST":
        if request.content_type == "application/json":
            data = json.loads(request.body.decode("utf-8"))
        else:
            data = request.POST

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone", "")
        company = data.get("company", "")
        subject = data.get("subject")
        inquiry_type = data.get("inquiry_type")
        message = data.get("message")

        full_message = f"""
📩 New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone}
Company: {company}
Subject: {subject}
Inquiry Type: {inquiry_type}

Message:
{message}
        """

        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "✅ Message sent successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"❌ Failed to send: {str(e)}"})

    return JsonResponse({"success": False, "message": "Invalid request"})
