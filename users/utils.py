# users/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_welcome_email(user):
    subject = "Welcome to Eduprompt!"
    html_message = render_to_string("emails/welcome_email.html", {"user": user})
    plain_message = strip_tags(html_message)
    from_email = None  # uses DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
