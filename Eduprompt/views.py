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


@csrf_exempt  # disable CSRF only for AJAX test; better to use CSRF token later
def send_message(request):
    if request.method == "POST":
        full_name = request.POST.get("fullName")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        development_type = request.POST.get("developmentType")
        website_type = request.POST.get("websiteType")
        client_location = request.POST.get("clientLocation")
        timeline = request.POST.get("timeline")
        message = request.POST.get("message")
        contact_method = request.POST.get("contactMethod")

        # Email content
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
            # Replace with your email + configured DEFAULT_FROM_EMAIL in settings.py
            send_mail(
                subject,
                body,
                "prospereze12345@email.com",  # FROM
                ["prospereze12345@gmail.com"],  # TO (your email)
                fail_silently=False,
            )
            return JsonResponse({"success": True, "message": "Message sent successfully"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})



def flyer_design(request):
    return render(request, 'flyer_design.html',)



@csrf_exempt
def contact_ajax(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        details = request.POST.get('details')
        budget = request.POST.get('budget', '')

        # Compose email message
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
                recipient_list=[settings.DEFAULT_FROM_EMAIL],  # your email
            )
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False}, status=500)


