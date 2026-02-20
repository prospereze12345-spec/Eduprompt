import logging
import requests
from threading import Thread
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def send_welcome_email_task(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("❌ User with id=%s not found.", user_id)
        return False

    if not user.email:
        logger.warning("⚠️ User %s has no email set. Skipping welcome email.", user.username)
        return False

    try:
        # Use your template
        html_content = render_to_string("emails/welcome_email.html", {"user": user})
        text_content = strip_tags(html_content)

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [user.email],
            "subject": "Welcome to Eduprompt!",
            "html": html_content,
            "text": text_content,
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code in (200, 202):
            logger.info("✅ Welcome email sent to %s (%s)", user.username, user.email)
            return True
        else:
            logger.error("❌ Resend error: %s - %s", response.status_code, response.text)
            return False

    except Exception as exc:
        logger.exception("❌ Error sending welcome email to %s: %s", user.email, exc)
        return False


def send_welcome_email_async(user_id):
    try:
        thread = Thread(target=send_welcome_email_task, args=(user_id,), daemon=True)
        thread.start()
        logger.info("📨 Email thread started for user_id=%s", user_id)
    except Exception as exc:
        logger.exception("❌ Failed to start email thread for user %s: %s", user_id, exc)
        raise