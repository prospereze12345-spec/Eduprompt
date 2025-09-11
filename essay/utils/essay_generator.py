import requests
from django.conf import settings

VALID_TYPES = ["expository", "narrative", "descriptive", "persuasive", "analytical"]

def generate_polished_essay(topic, essay_type="expository"):
    essay_type = essay_type.lower()
    if essay_type not in VALID_TYPES:
        essay_type = "expository"

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are a college student writing an essay. "
        "Write naturally, imperfectly, as if a human wrote it. "
        "Do not use symbols, markers, lists, or headings (no ###, ***, //, [], brackets). "
        "Include minor sentence fragments, casual phrasing, personal reflections, or digressions. "
        "Vary sentence lengths, use parentheses, dashes, or ellipses occasionally. "
        "Use simple vocabulary that is easy to read. "
        "Include exactly 3 realistic references at the end, formatted like a student would, "
        "slightly inconsistent but plausible. "
        f"Essay type: {essay_type}. Topic: {topic}."
    )

    payload = {
        "model": "glm-4.5",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Write a {essay_type} essay on the topic: {topic}. Include introduction, body, and conclusion. Add exactly 3 human-like references at the end."}
        ],
        "max_tokens": 1100,
        "temperature": 0.85
    }

    # === Step 1: Zhipu API ===
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Could not reach Zhipu API: {e}")

    if "choices" not in data or not data["choices"]:
        raise RuntimeError(f"Zhipu API returned no content: {data}")

    draft_essay = data["choices"][0]["message"]["content"]

    # === Step 2: LanguageTool polish ===
    lt_url = "http://localhost:8081/v2/check"
    lt_payload = {"language": "en-US", "text": draft_essay}

    try:
        lt_response = requests.post(lt_url, data=lt_payload, timeout=10)
        lt_data = lt_response.json()
    except requests.exceptions.RequestException as e:
        print(f"LanguageTool error: {e}")
        return draft_essay

    polished_text = draft_essay
    try:
        if "matches" in lt_data:
            for match in reversed(lt_data["matches"]):
                replacements = match.get("replacements", [])
                if replacements:
                    offset = match["offset"]
                    length = match["length"]
                    replacement = replacements[0]["value"]
                    polished_text = polished_text[:offset] + replacement + polished_text[offset + length:]
    except Exception as e:
        print(f"Error applying LanguageTool suggestions: {e}")
        polished_text = draft_essay

    return polished_text
