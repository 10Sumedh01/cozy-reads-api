from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.cache import invalidate_user_goals_cache

from .models import ReadingGoal


@receiver(post_save, sender=ReadingGoal)
@receiver(post_delete, sender=ReadingGoal)
def on_goal_change(sender, instance, **kwargs):
    invalidate_user_goals_cache(instance.user_id)
