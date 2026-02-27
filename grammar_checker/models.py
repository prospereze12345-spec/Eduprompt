from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Subscription fields
    is_subscribed = models.BooleanField(default=False)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    flutterwave_tx_ref = models.CharField(max_length=100, null=True, blank=True)

    # Daily usage tracking
    daily_check_count = models.IntegerField(default=0)
    last_check_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    @property
    def is_active_subscriber(self):
        """
        Returns True if the user has an active subscription.
        Automatically expires subscription if end date has passed.
        """
        if self.is_subscribed and self.subscription_end:
            if timezone.now() <= self.subscription_end:
                return True
            else:
                # Auto-expire subscription
                self.is_subscribed = False
                self.save(update_fields=["is_subscribed"])
        return False

    def reset_daily_limit_if_needed(self):
        """
        Resets daily check counter if it's a new day.
        """
        now = timezone.now()
        if not self.last_check_date or self.last_check_date.date() != now.date():
            self.daily_check_count = 0
            self.last_check_date = now
            self.save(update_fields=["daily_check_count", "last_check_date"])

