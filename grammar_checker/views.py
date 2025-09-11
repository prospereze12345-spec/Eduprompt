from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def grammar_checker(request):
    """
    Grammar checker using self-hosted LanguageTool only.
    Supports many languages including some African ones (af, sw).
    """
    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        language = request.POST.get("language", "en-US")  # default English
        auto_correct = request.POST.get("auto_correct", "false") == "true"

        if not text:
            return JsonResponse({"error": "No text provided"}, status=400)

        # Optional: Validate language against supported list
        supported_languages = [
            # African languages
            "af", "sw",
            # English
            "en-US", "en-GB", "en-AU", "en-CA", "en-NZ", "en-ZA",
            # French
            "fr", "fr-FR", "fr-CA", "fr-BE", "fr-CH",
            # German
            "de", "de-DE", "de-AT", "de-CH",
            # Spanish
            "es", "es-ES", "es-MX", "es-AR", "es-CO", "es-CL",
            # Other languages
            "it", "it-IT", "pt", "pt-PT", "pt-BR", "nl", "nl-NL", "nl-BE",
            "sv", "fi", "da", "no", "pl", "ru", "ro", "hu", "cs", "sk",
            "uk", "sl", "hr", "bg", "ja", "zh", "tr", "id"
        ]
        if language not in supported_languages:
            return JsonResponse({"error": f"Language '{language}' not supported"}, status=400)

        try:
            lt_response = requests.post(
                settings.LANGUAGETOOL_API,
                data={"text": text, "language": language},
                timeout=30
            )
            lt_response.raise_for_status()
            lt_data = lt_response.json()
            matches = lt_data.get("matches", [])

            corrected_text = text
            if auto_correct and matches:
                corrected_chars = list(text)
                shift = 0
                for match in matches:
                    replacements = match.get("replacements", [])
                    if replacements:
                        repl = replacements[0]["value"]
                        offset = match["offset"] + shift
                        length = match["length"]
                        corrected_chars[offset:offset+length] = list(repl)
                        shift += len(repl) - length
                corrected_text = "".join(corrected_chars)

            return JsonResponse({
                "matches": matches,
                "corrected_text": corrected_text if auto_correct else None,
                "source": "lt"
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"LanguageTool API request failed: {e}"}, status=500)

    return render(request, "grammar_checker.html")
