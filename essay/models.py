from django.db import models


class Essay(models.Model):
    ESSAY_TYPES = [
        ("narrative", "Narrative"),
        ("descriptive", "Descriptive"),
        ("expository", "Expository"),
        ("persuasive", "Persuasive"),
        ("analytical", "Analytical"),
    ]

    topic = models.CharField(max_length=300)
    essay_type = models.CharField(max_length=20, choices=ESSAY_TYPES, default="narrative")
    content = models.TextField()
    language_code = models.CharField(max_length=10, default="en")
    photo = models.ImageField(upload_to="essay_photos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_essay_type_display()} – {self.topic[:50]}"
