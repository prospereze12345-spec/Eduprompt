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
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)  # Basic, Standard, Unlimited
    essays_per_month = models.IntegerField(default=5)
    price_ngn = models.IntegerField(default=0)
    price_usd = models.FloatField(default=0)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan_code = models.CharField(max_length=50, blank=True, null=True)
    essays_used = models.IntegerField(default=0)
    essays_limit = models.IntegerField(blank=True, null=True)  # null = unlimited
    free_trial_used = models.BooleanField(default=False)
    start_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    def is_active(self):
        if not self.plan_code:
            return False
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False
        return True

    def essays_left(self):
        if self.essays_limit is None:  # Unlimited
            return "∞"
        return max(0, self.essays_limit - self.essays_used)
