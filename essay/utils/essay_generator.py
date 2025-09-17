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


def generate_polished_essay(topic: str, essay_type: str, lang: str):
    essay_type = essay_type.lower()
    if essay_type not in VALID_TYPES:
        essay_type = "expository"

    lang_name, lt_code = LANGUAGE_MAP.get(lang, ("English", "en-US"))

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        f"You are an expert college student writing a highly engaging, human-like essay in {lang_name}. "
        f"Essay type: {essay_type}. Topic: {topic}. "
        f"Write approximately {FIXED_WORD_COUNT} words including {FIXED_CITATIONS} realistic references at the end. "
        "Use natural, emotional, easy-to-read language. Avoid bullet points, headings, and symbols like */#@. "
        "Make it feel like a real student wrote it."
    )

    payload = {
        "model": "glm-4.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Write the essay in {lang_name}, ~{FIXED_WORD_COUNT} words, human-like, ending with {FIXED_CITATIONS} references."
                ),
            },
        ],
        "max_tokens": min(8000, FIXED_WORD_COUNT * 4),
        "temperature": 0.9,
    }

    # --- Call Zhipu API ---
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        draft_essay = data["choices"][0]["message"]["content"]
    except Exception as e:
        # Fallback: return a simple essay if API fails
        print(f"Zhipu API failed: {e}")
        return f"⚠ Essay generation failed. Topic: {topic}. Please try again."

    # --- Optional: LanguageTool polishing ---
    polished_text = draft_essay
    lt_url = "http://localhost:8081/v2/check"
    lt_payload = {"language": lt_code, "text": draft_essay}

    try:
        lt_response = requests.post(lt_url, data=lt_payload, timeout=10)
        lt_data = lt_response.json()
        if "matches" in lt_data:
            for match in reversed(lt_data["matches"]):
                replacements = match.get("replacements", [])
                if replacements:
                    offset = match["offset"]
                    length = match["length"]
                    replacement = replacements[0]["value"]
                    polished_text = polished_text[:offset] + replacement + polished_text[offset + length:]
    except Exception as e:
        print(f"LanguageTool skipped for {lt_code}: {e}")
        polished_text = draft_essay  # fallback to unpolished draft

    # --- Minimal validation ---
    words_in_essay = len(polished_text.split())
    if words_in_essay < int(FIXED_WORD_COUNT * 0.5):
        polished_text += "\n\n[Content may be incomplete due to API limits]"

    # Ensure citations exist
    refs_found = polished_text.lower().count("http") + polished_text.lower().count("ref")
    if refs_found < FIXED_CITATIONS:
        polished_text += f"\n\n[Expected {FIXED_CITATIONS} references missing]"

    return polished_text
