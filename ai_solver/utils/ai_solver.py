# utils/ai_solver.py
import requests
from django.conf import settings

def solve_with_zhipu(problem, subject="math", max_words=300, mode="explain", max_tokens=1000, timeout=60):
    """
    STEM-focused step-by-step solver.

    Parameters:
    - problem: str, the question
    - subject: "math", "physics", "chemistry"
    - max_words: approximate word limit
    - mode: "explain" (plain steps) or "equations" (mostly formulas)
    - max_tokens: for API
    - timeout: request timeout in seconds

    Returns: str solution with practical, clear step-by-step explanation
    """

    system_prompt = (
        f"You are a professional {subject} tutor and solver. "
        "Provide detailed, step-by-step solutions in separate paragraphs. "
        "Explain each step as if teaching a beginner. "
        "Use correct formulas, units, and calculations. "
        "If mode is 'equations', focus on formulas with minimal text. "
        "If mode is 'explain', write clear and concise sentences for each step. "
        f"The answer must be accurate and no longer than {max_words} words. "
        "Do not include markdown, code fences, asterisks, slashes, or decorative symbols. "
        "Each step should be its own paragraph with practical explanation of why the step is done."
    )

    user_prompt = f"Problem: {problem}\nMode: {mode}"

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "glm-4.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,  # low randomness for precise answers
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        solution = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return solution
    except Exception as e:
        return f"⚠️ Zhipu API error: {e}"
