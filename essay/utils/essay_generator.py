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

    # --- Tailored instructions by essay type ---
    type_instructions = {
        "narrative": "Write like a storyteller, in first-person or third-person, with vivid scenes and emotions.",
        "descriptive": "Use sensory details (sight, sound, touch, taste, smell) to paint a vivid picture.",
        "expository": "Be clear, logical, and informative, explaining the topic step by step.",
        "persuasive": "Take a clear position, provide strong arguments, counterarguments, and end with a call to action.",
        "analytical": "Break down the topic into parts, analyze causes and effects, and provide critical insights.",
    }
    type_style = type_instructions.get(essay_type, "Be clear, structured, and academic.")

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = (
        f"You are an expert essay writer. "
        f"Write a plagiarism-free, highly original {essay_type} essay in {lang_name}. "
        f"Topic: '{topic}'. "
        f"Target length: about {FIXED_WORD_COUNT} words. "
        f"Style guide: {type_style} "
        "Organize the essay into multiple clear paragraphs (4–7). "
        "Do not use bullet points, numbered lists, or symbols like #, *, /. "
        "The essay must read naturally, as if written by a real student. "
        "Avoid repeating the same sentence to increase word count. "
        f"At the end, include exactly {FIXED_CITATIONS} scholarly references under a section titled 'References:'. "
        "References should look realistic (books, academic journals, or articles)."
    )

    payload = {
        "model": "glm-4.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Please write a {essay_type} essay in {lang_name} on '{topic}'. "
                    f"It must be about {FIXED_WORD_COUNT} words, structured into good paragraphs, "
                    f"and end with exactly {FIXED_CITATIONS} references under 'References:'. "
                    "Avoid strange characters or formatting."
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
        print(f"Zhipu API failed: {e}")
        return f"This is a fallback essay on '{topic}'.\n\n(Unable to reach essay API. Please retry later.)"

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
        polished_text = draft_essay

    # --- Post-processing cleanup ---
    # Remove repeated filler lines
    lines = polished_text.splitlines()
    seen = set()
    cleaned_lines = []
    for line in lines:
        if line.strip() not in seen:
            cleaned_lines.append(line)
            seen.add(line.strip())
    polished_text = "\n".join(cleaned_lines)

    # Fix references heading
    polished_text = polished_text.replace("## References", "References").replace("# References", "References")

    # Auto paragraph split if text is too blocky
    if polished_text.count("\n\n") < 3:  # less than 3 breaks
        sentences = polished_text.split(". ")
        chunk_size = max(4, len(sentences) // 5)  # about 5–6 paragraphs
        paragraphs = []
        for i in range(0, len(sentences), chunk_size):
            paragraphs.append(". ".join(sentences[i:i+chunk_size]))
        polished_text = "\n\n".join(paragraphs)

    # Ensure references section exists
    if "references:" not in polished_text.lower():
        polished_text += "\n\nReferences:\n"
        for i in range(1, FIXED_CITATIONS + 1):
            polished_text += f"{i}. [Reference placeholder]\n"

    return polished_text
