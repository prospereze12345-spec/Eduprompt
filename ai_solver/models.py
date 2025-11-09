from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class AISolverSubscription(models.Model):
    PLAN_CHOICES = [
        ("trial", "Free Trial (3 solves)"),
        ("basic_naira", "Basic (₦1,500 / 20 solves / 30 days)"),
        ("standard_naira", "Standard (₦4,500 / 70 solves / 30 days)"),
        ("unlimited_naira", "Unlimited (₦12,000 / 30 days)"),
        ("basic_usd", "Basic ($3 / 20 solves / 30 days)"),
        ("standard_usd", "Standard ($8 / 70 solves / 30 days)"),
        ("unlimited_usd", "Unlimited ($20 / 30 days)"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default="trial")

    solver_used = models.IntegerField(default=0)
    solver_limit = models.IntegerField(default=3)  # default = free trial

    start_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField(blank=True, null=True)

    active = models.BooleanField(default=True)  # free trial is active at signup

    def activate_plan(self, plan_code, duration_days=30):
        """
        Activate or upgrade to a paid plan.
        Resets usage and sets solver_limit based on plan.
        """
        self.plan = plan_code
        self.start_date = timezone.now()
        self.expiry_date = timezone.now() + timedelta(days=duration_days)
        self.active = True

        # --- Limits ---
        if "basic" in plan_code:
            self.solver_limit = 20
        elif "standard" in plan_code:
            self.solver_limit = 50
        elif "unlimited" in plan_code:
            self.solver_limit = None  # unlimited solves
        else:
            self.solver_limit = 3  # fallback to trial

        self.solver_used = 0  # reset usage when switching plans
        self.save()

    def is_active(self):
        """
        Check if subscription is still valid.
        Expired → inactive automatically.
        Admin/superuser is always active.
        """
        if self.user.is_superuser:
            return True
        if not self.active:
            return False
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False
        return True

    def solver_left(self):
        """
        Remaining solver attempts.
        Returns ∞ for unlimited plans.
        Admin/superuser always has unlimited.
        """
        if self.user.is_superuser:
            return "∞"
        if self.solver_limit is None:
            return "∞"
        return max(0, self.solver_limit - self.solver_used)

    def use_solver(self):
        """
        Use one solver attempt.
        Returns False if limit reached.
        Admin/superuser always allowed.
        """
        if self.user.is_superuser:
            return True
        if self.solver_limit is not None and self.solver_used >= self.solver_limit:
            return False
        self.solver_used += 1
        self.save()
        return True

    def __str__(self):
        return f"{self.user} - {self.plan} ({self.solver_used}/{self.solver_limit or '∞'})"
