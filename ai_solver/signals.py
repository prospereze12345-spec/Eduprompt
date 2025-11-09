# ai_solver/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import AISolverSubscription  # your subscription model

User = get_user_model()

@receiver(post_save, sender=User)
def create_subscription_and_admin(sender, instance, created, **kwargs):
    """
    Creates subscription for every new user.
    Makes the first user superuser with unlimited access.
    """
    if created:
        # Create subscription/profile
        subscription, _ = AISolverSubscription.objects.get_or_create(user=instance)

        # Make first user admin + unlimited access
        if User.objects.count() == 1:
            instance.is_staff = True
            instance.is_superuser = True
            instance.save()

            subscription.solver_limit = None  # unlimited solves
            subscription.active = True
            subscription.save()
