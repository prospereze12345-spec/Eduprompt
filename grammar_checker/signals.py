from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Import UserProfile lazily inside the function to avoid circular imports
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import UserProfile  # import here to prevent circular import
        UserProfile.objects.create(user=instance)
