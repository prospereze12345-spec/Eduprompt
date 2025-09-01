
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    number = models.CharField(max_length=20)
    country = models.CharField(max_length=100, blank=True, null=True)  # optional

    def __str__(self):
        return self.full_name or self.user.username





