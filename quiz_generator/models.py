from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class QuizSubscription(models.Model):
    PLAN_CHOICES = [
        ("trial", "Free Trial (3 quizzes)"),
        ("basic_ng", "Basic (₦1,200 / 20 quizzes / 30 days)"),
        ("standard_ng", "Standard (₦2,800 / 50 quizzes / 30 days)"),
        ("unlimited_ng", "Unlimited (₦7,500 / 30 days)"),
        ("basic_usd", "Basic ($2 / 20 quizzes / 30 days)"),
        ("standard_usd", "Standard ($5 / 50 quizzes / 30 days)"),
        ("unlimited_usd", "Unlimited ($10 / 30 days)"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default="trial")

    quizzes_used = models.IntegerField(default=0)
    quizzes_limit = models.IntegerField(default=3)  # free trial limit

    start_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    active = models.BooleanField(default=True)  # trial active at signup

    def activate_plan(self, plan_code, duration_days=30):
        """
        Activate or upgrade to a plan.
        Resets usage and sets quizzes_limit based on plan.
        """
        self.plan = plan_code
        self.start_date = timezone.now()
        self.expiry_date = timezone.now() + timedelta(days=duration_days)
        self.active = True

        # --- Limits ---
        if "basic" in plan_code:
            self.quizzes_limit = 20
        elif "standard" in plan_code:
            self.quizzes_limit = 50
        elif "unlimited" in plan_code:
            self.quizzes_limit = None  # unlimited quizzes
        else:
            self.quizzes_limit = 3  # fallback to trial

        self.quizzes_used = 0  # reset usage when switching plans
        self.save()

    def is_active(self):
        """
        Check if subscription is still valid.
        Expired → inactive automatically.
        """
        if not self.active:
            return False
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False
        return True

    def quizzes_left(self):
        """
        Remaining quizzes attempts.
        Returns "Unlimited" for unlimited plans.
        """
        if self.quizzes_limit is None:
            return "Unlimited"
        return max(0, self.quizzes_limit - self.quizzes_used)

    def use_quiz(self):
        """
        Use one quiz attempt.
        Returns False if limit reached.
        """
        if self.quizzes_limit is not None and self.quizzes_used >= self.quizzes_limit:
            return False
        self.quizzes_used += 1
        self.save()
        return True

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.quizzes_used}/{self.quizzes_limit or 'Unlimited'})"

# quiz_generator/models.py

from django.db import models
from django.contrib.auth.models import User

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    quizzes_used = models.IntegerField(default=0)
    quizzes_limit = models.IntegerField(default=10)  # None = Unlimited
    active = models.BooleanField(default=True)

    def is_active(self):
        return self.active

    def quizzes_left(self):
        if self.quizzes_limit is None:
            return None  # Unlimited
        return max(0, self.quizzes_limit - self.quizzes_used)

    def use_quiz(self):
        if self.quizzes_limit is None:
            return  # Unlimited
        self.quizzes_used += 1
        self.save()

    def __str__(self):
        return f"{self.user.username} Subscription"
