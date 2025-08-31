from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def grammar_checker(request):
    """
    Grammar checker view:
    - Uses self-hosted LanguageTool for grammar detection.
    - Uses OpenRouter GPT model for AI rewriting if auto_correct is requested.
    """
    if request.method == "POST":
        text = request.POST.get("text", "")
        language = request.POST.get("language", "en-US")
        auto_correct = request.POST.get("auto_correct", "false") == "true"

        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)

        try:
            # Step 1: LanguageTool detection
            lt_response = requests.post(
                settings.LANGUAGETOOL_API,
                data={"text": text, "language": language},
                timeout=30
            )
            lt_data = lt_response.json()
            matches = lt_data.get("matches", [])

            if auto_correct:
                # Step 2: Apply LT corrections
                corrected_text = list(text)
                shift = 0
                for match in matches:
                    if match.get("replacements"):
                        repl = match["replacements"][0]["value"]
                        offset = match["offset"] + shift
                        length = match["length"]
                        corrected_text[offset:offset+length] = list(repl)
                        shift += len(repl) - length
                corrected_text = "".join(corrected_text)

                # Step 3: Optional OpenRouter AI rewrite
                if getattr(settings, "OPENROUTER_API_KEY", None):
                    try:
                        or_response = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                                "Content-Type": "application/json",
                            },
                            json={
                                "model": "gpt-4o-mini",
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": "You are a grammar and style corrector. Rewrite the text with proper grammar and clarity without changing the meaning."
                                    },
                                    {"role": "user", "content": corrected_text}
                                ],
                            },
                            timeout=60
                        )
                        or_data = or_response.json()
                        if "choices" in or_data and len(or_data["choices"]) > 0:
                            ai_text = or_data["choices"][0]["message"]["content"]
                            return JsonResponse({
                                "corrected_text": ai_text.strip(),
                                "matches": matches,
                                "source": "openrouter+lt"
                            })
                    except Exception as e:
                        # fallback if OpenRouter fails
                        return JsonResponse({
                            "corrected_text": corrected_text,
                            "matches": matches,
                            "warning": f"OpenRouter fallback: {str(e)}",
                            "source": "lt"
                        })

                # Fallback: LT-only correction
                return JsonResponse({
                    "corrected_text": corrected_text,
                    "matches": matches,
                    "source": "lt"
                })

            # Normal check mode
            return JsonResponse({"matches": matches, "source": "lt"})

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"LanguageTool API error: {e}"}, status=500)

    return render(request, "grammar_checker.html", {
        "AFRICAN_LANGUAGES": getattr(settings, "AFRICAN_LANGUAGES", [])
    })
