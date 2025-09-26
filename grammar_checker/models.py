from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_subscribed = models.BooleanField(default=False)
    subscription_start = models.DateTimeField(null=True, blank=True)
    subscription_end = models.DateTimeField(null=True, blank=True)
    flutterwave_tx_ref = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    @property
    def is_active_subscriber(self):
        """Return True if user has an active subscription."""
        if self.is_subscribed and self.subscription_end:
            if timezone.now() <= self.subscription_end:
                return True
            else:
                # auto-expire if end date has passed
                self.is_subscribed = False
                self.save(update_fields=["is_subscribed"])
        return False

