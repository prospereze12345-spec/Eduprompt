import os
import requests
from django.conf import settings


def generate_quiz_from_text(
    study_text: str,
    quiz_type: str = "mixed",
    difficulty: str = "medium",
    max_questions: int = 10,
    model: str = "glm-4-air",  # ✅ Supported Zhipu model
    max_tokens: int = 900,
    timeout: int = 30,
    language: str = "English",  # 🌍 New: target language
) -> str:
    """
    Generate a professional quiz from study material using Zhipu API.

    Returns:
        str: Quiz text OR error message (⚠️ ...).
    """

    # 🚨 1. Validate input
    if not study_text or not study_text.strip():
        return "⚠️ No study material provided."

    # 🔑 2. Get API key (settings OR env fallback)
    api_key = getattr(settings, "ZHIPU_API_KEY", None) or os.getenv("ZHIPU_API_KEY")
    if not api_key or api_key.strip() == "":
        return "⚠️ Missing ZHAPU_API_KEY. Please set it in settings.py or .env."

    # ✅ 3. Cap max_questions between 1–10
    try:
        max_questions = int(max_questions)
    except Exception:
        max_questions = 10
    if max_questions <= 0 or max_questions > 10:
        max_questions = 10

    # 📝 4. System prompt (STRICT)
    system_prompt = (
        "You are an expert academic quiz generator. "
        f"Always generate quizzes in {language}. "
        "Produce exam-ready, unambiguous questions and answers. "
        "Do NOT include explanations, code snippets, or /* comments. "
        "Format output as a clean numbered list for easy display in a web app. "
        f"Generate EXACTLY {max_questions} questions, no more, no less."
    )

    # 🎯 5. User prompt
    user_prompt = f"""
Generate EXACTLY {max_questions} {quiz_type} questions from the study material below.

Guidelines:
- Language: {language}
- Difficulty: {difficulty}
- MCQ: include 4 options (A, B, C, D) and clearly mark the correct answer.
- True/False: provide the statement and the correct answer.
- Short Answer: provide a 1–3 sentence solution.
- Include factual recall, comprehension, and applied reasoning.

Study Material:
\"\"\"{study_text.strip()}\"\"\" 
"""

    # 🌍 6. API request config
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    # 🚨 7. Send request
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"⚠️ Request to Zhipu API failed: {e}"

    # ✅ 8. Parse response
    try:
        data = resp.json()
    except Exception:
        return f"⚠️ Invalid JSON from Zhipu API: {resp.text[:300]}"

    try:
        if "choices" in data and data["choices"]:
            content = (
                data["choices"][0].get("message", {}).get("content", "").strip()
            )
            if content:
                # Remove stray code-style comments if any
                cleaned = content.replace("/*", "").replace("*/", "")
                return cleaned
            return "⚠️ Zhipu returned an empty response."
        return f"⚠️ Zhipu API error: {data}"
    except Exception as e:
        return f"⚠️ Error parsing Zhipu API response: {e}"




# quiz_generator/utils.py

import os
import requests
from django.conf import settings
from quiz_generator.models import Subscription  # ✅ fixed import


def generate_quiz_from_text(
    study_text: str,
    quiz_type: str = "mixed",
    difficulty: str = "medium",
    max_questions: int = 10,
    model: str = "glm-4-air",
    max_tokens: int = 900,
    timeout: int = 30,
    language: str = "English",
) -> str:
    """
    Generate a professional quiz from study material using Zhipu API.
    Returns a clean quiz text OR an error string starting with ⚠️.
    """

    if not study_text or not study_text.strip():
        return "⚠️ No study material provided."

    api_key = getattr(settings, "ZHIPU_API_KEY", None) or os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return "⚠️ Missing ZHIPU_API_KEY. Please set it in settings.py or .env."

    try:
        max_questions = int(max_questions)
    except Exception:
        max_questions = 10
    if max_questions <= 0 or max_questions > 10:
        max_questions = 10

    system_prompt = (
        f"You are an expert academic quiz generator. Always generate quizzes in {language}. "
        "Produce exam-ready, unambiguous questions and answers. "
        "Do NOT include explanations, code snippets, or comments. "
        f"Generate EXACTLY {max_questions} questions, no more, no less."
    )

    user_prompt = f"""
Generate EXACTLY {max_questions} {quiz_type} questions from the study material below.

Guidelines:
- Language: {language}
- Difficulty: {difficulty}
- MCQ: include 4 options (A, B, C, D) and clearly mark the correct answer.
- True/False: provide the statement and the correct answer.
- Short Answer: provide a 1–3 sentence solution.

Study Material:
\"\"\"{study_text.strip()}\"\"\" 
"""

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"⚠️ Request to Zhipu API failed: {e}"

    try:
        data = resp.json()
        if "choices" in data and data["choices"]:
            content = data["choices"][0].get("message", {}).get("content", "").strip()
            if content:
                return content.replace("/*", "").replace("*/", "")
            return "⚠️ Zhipu returned an empty response."
        return f"⚠️ Zhipu API error: {data}"
    except Exception as e:
        return f"⚠️ Error parsing Zhipu API response: {e}"


def _check_quiz_access(user):
    """
    Checks if a user has access to generate a quiz based on subscription plan.
    Returns (allowed: bool, subscription: Subscription|None, message: str).
    """

    if not user.is_authenticated:
        return False, None, "Please login first."

    try:
        sub = Subscription.objects.filter(user=user).first()
        if not sub:
            # Give first-time users a free trial of 1 quiz
            sub = Subscription.objects.create(
                user=user, plan="free", quizzes_used=0, quizzes_per_month=1
            )
            return True, sub, "Free trial granted (1 quiz available)."

        if not sub.is_active():
            return False, sub, "Your subscription has expired."

        left = sub.quizzes_left()
        if left is None:  # Unlimited plan
            return True, sub, "Access granted (Unlimited)."
        if left > 0:
            return True, sub, f"Access granted ({left} quizzes left)."

        return False, sub, "You have no quizzes left this month. Please upgrade."

    except Exception as e:
        return False, None, f"⚠️ Subscription check error: {e}"

