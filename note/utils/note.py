import requests
from django.conf import settings

def generate_study_note(
    subject: str,
    topic: str,
    level: str = "general",   # waec, jamb, university, or general
    max_words: int = 600,
    style: str = "student_friendly",
    timeout: int = 60
) -> str:
    """
    Generate a clear, well-structured, human-friendly study note for a given subject and topic.
    Adapted for WAEC, JAMB, or university level.
    Structure: Introduction, Key Definitions, Formulas, Examples, Tips, Mistakes.
    Written in full paragraphs, relatable, conversational, and student/teacher-friendly.
    """

    level_instruction = ""
    if level.lower() == "waec":
        level_instruction = "Make the explanations simple, with clear examples aligned to WAEC standards. Use common exam-style examples Nigerian students face."
    elif level.lower() == "jamb":
        level_instruction = "Structure the explanation in a way that prepares students for JAMB exams. Include exam-focused examples, shortcuts, and common tricky areas."
    elif level.lower() == "university":
        level_instruction = "Write with more depth suitable for university students. Use advanced but clear explanations, include formulas, derivations, and real academic examples."
    else:
        level_instruction = "Keep the note clear and balanced so it can help both students and teachers."

    system_prompt = (
        f"You are an expert {subject} tutor in Nigeria. "
        "Your task is to create a structured, accurate, and engaging study note. "
        "Organize it in this order: introduction, key definitions, formulas, examples, tips, and common mistakes. "
        "Write naturally, like a teacher guiding students step by step. "
        "Avoid bullet points, markdown, hashtags, or decorative symbols. "
        "Use full paragraphs, smooth flow, and simple English where possible. "
        "Relate concepts to real-life situations Nigerian students can understand. "
        f"{level_instruction} "
        f"The note must not exceed {max_words} words."
    )

    user_prompt = f"Generate a study note on '{topic}' in {subject}. Style: {style}."

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
        "max_tokens": 1000,   # enough for detailed ~500–600 word notes
        "temperature": 0.65,  # make it more human-like and less robotic
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        note_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not note_text:
            return "⚠️ Note generator returned empty content."
        
        return note_text
    except Exception as e:
        return f"⚠️ Note generator error: {e}"

