# utils/ai_solver.py
import os
import time
import requests
from django.conf import settings


def solve_with_zhipu(
    problem: str,
    subject: str = "math",
    max_words: int = 300,
    mode: str = "explain",
    max_tokens: int = 1000,
    timeout: int = 60,
    language: str = "English",
    retries: int = 3,   # 🔹 number of retry attempts
    backoff: float = 2  # 🔹 backoff multiplier in seconds
) -> str:
    """
    STEM-focused step-by-step solver via Zhipu (GLM series).
    Forces output in the chosen language (English, French, Igbo, Yoruba, Hausa, etc.).
    Retries automatically on transient connection errors.
    """

    if not problem or not str(problem).strip():
        return "⚠️ No problem provided."

    api_key = getattr(settings, "ZHIPU_API_KEY", None) or os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return "⚠️ Missing ZHIPU_API_KEY. Please set it in settings.py or environment."

    language = (language or "English").strip() or "English"

    system_prompt = (
        f"You are a highly skilled {subject} tutor. "
        f"CRITICAL RULE: Respond ONLY in {language}. "
        f"Do not mix English with {language}, unless a term cannot be translated (in which case explain it briefly). "
        "Provide the solution step by step, with each step in its own short paragraph. "
        "Make explanations clear and beginner-friendly. "
        "Always use correct formulas, units, and calculations. "
        f"Mode: {mode}. Keep the response under {max_words} words. "
        "Do NOT use markdown, bullet points, asterisks, or decorative symbols."
    )

    user_prompt = (
        f"Problem:\n{problem}\n\n"
        f"Mode: {mode}\nLanguage: {language}\n\n"
        "Now produce a full, step-by-step explanation in the target language."
    )

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "glm-4.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }

    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()

            choices = data.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                content = message.get("content", "").strip()
                if content:
                    return content
                return f"⚠️ Zhipu returned an empty solution in {language}."

            if "error" in data:
                return f"⚠️ Zhipu API error: {data['error']}"
            if "message" in data:
                return f"⚠️ Zhipu API message: {data['message']}"

            return f"⚠️ Unexpected Zhipu response: {str(data)[:300]}"

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < retries:
                wait = backoff * attempt
                print(f"⚠️ Connection issue, retrying in {wait}s... ({attempt}/{retries})")
                time.sleep(wait)
            else:
                return f"⚠️ Zhipu API request failed after {retries} attempts: {e}"

        except requests.exceptions.RequestException as e:
            return f"⚠️ Zhipu API request failed: {e}"

        except Exception as e:
            return f"⚠️ Unexpected error: {e}"
