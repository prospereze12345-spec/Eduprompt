import requests
from django.conf import settings

VALID_TYPES = ["narrative", "descriptive", "expository", "persuasive", "analytical"]
LANGUAGE_MAP = {
    "en": ("English", "en-US"),
    "yo": ("Yoruba", "yo"),
    "ig": ("Igbo", "ig"),
    "ha": ("Hausa", "ha"),
    "ar": ("Arabic", "ar"),
    "zu": ("Zulu", "zu"),
    "sw": ("Swahili", "sw"),
    "fr": ("French", "fr-FR"),
}

FIXED_WORD_COUNT = 800
FIXED_CITATIONS = 3


def clean_repeated_sentences(text: str) -> str:
    """Remove duplicate sentences while keeping order."""
    sentences = text.split(". ")
    seen = set()
    cleaned = []
    for s in sentences:
        s_clean = s.strip()
        if s_clean and s_clean not in seen:
            cleaned.append(s_clean)
            seen.add(s_clean)
    return ". ".join(cleaned)


def generate_polished_essay(topic: str, essay_type: str, lang: str) -> str:
    """
    Generate a high-quality 800-word essay without caching.
    """

    essay_type = essay_type.lower()
    if essay_type not in VALID_TYPES:
        essay_type = "expository"

    lang_name, lt_code = LANGUAGE_MAP.get(lang, ("English", "en-US"))

    type_instructions = {
        "narrative": "Write like a storyteller with vivid scenes and emotions.",
        "descriptive": "Use sensory details (sight, sound, touch, taste, smell) to paint a vivid picture.",
        "expository": "Be clear, logical, and informative, explaining the topic step by step.",
        "persuasive": "Take a clear position, provide strong arguments, counterarguments, and end with a call to action.",
        "analytical": "Break down the topic into parts, analyze causes and effects, and provide critical insights.",
    }
    type_style = type_instructions.get(essay_type, "Be clear, structured, and academic.")

    # --- System prompt ---
    system_prompt = (
        f"You are a world-class academic essay writer. Your task is to write a "
        f"flawless, highly original {essay_type} essay in {lang_name} on '{topic}'. "
        f"Target length: ~{FIXED_WORD_COUNT} words. Style: {type_style}\n\n"
        "Instructions:\n"
        "1. Use professional, mature, and engaging academic tone.\n"
        "2. Avoid plagiarism and repeated phrases or sentences.\n"
        "3. Structure essay into 5–7 paragraphs: intro, body, conclusion.\n"
        "4. Each body paragraph presents a unique idea with examples or citations.\n"
        "5. Smooth transitions between paragraphs.\n"
        "6. Avoid bullet points, lists, or special symbols.\n"
        f"7. Include exactly {FIXED_CITATIONS} realistic references under 'References:' at the end.\n"
        "8. Vary vocabulary and sentence structures.\n"
        "9. Ensure essay reads naturally and professionally.\n"
        "10. Correct grammar, punctuation, and spelling.\n"
        "Now generate the essay."
    )

    payload = {
        "model": "glm-4.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write the essay on '{topic}' in {lang_name}."},
        ],
        "max_tokens": min(8000, FIXED_WORD_COUNT * 4),
        "temperature": 0.9,
    }

    try:
        response = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
        draft_essay = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"ZHAPI API failed: {e}")
        return f"This is a fallback essay on '{topic}'.\n(Unable to reach essay API. Please try again later.)"

    # --- Remove repeated sentences ---
    polished_text = clean_repeated_sentences(draft_essay)

    # --- Ensure references section ---
    if "references:" not in polished_text.lower():
        polished_text += "\n\nReferences:\n"
        for i in range(1, FIXED_CITATIONS + 1):
            polished_text += f"{i}. [Reference placeholder]\n"

    return polished_text