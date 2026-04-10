from seo_pages.models import SeoPage
from seo_pages.data import PAGES   # your data.py file

for slug, data in PAGES.items():
    SeoPage.objects.update_or_create(
        slug=slug,
        defaults={
            "group": data.get("group", ""),
            "keyword": data.get("keyword", ""),
            "title": data.get("title", ""),
            "meta_description": data.get("meta_description", ""),
            "h1": data.get("h1", ""),
            "intro": data.get("intro", ""),
            "problem": data.get("problem", ""),
            "solution": data.get("solution", ""),
            "benefits": data.get("benefits", []),
            "use_case": data.get("use_case", ""),
            "faq": data.get("faq", []),
            "cta": data.get("cta", ""),
        }
    )

print("DONE: SEO pages imported")