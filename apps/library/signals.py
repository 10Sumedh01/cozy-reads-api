from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.core.cache import invalidate_user_stats_cache

from .models import ReadingSession, UserBook

# Maintain backwards compatibility for any external callers
invalidate_stats_cache = invalidate_user_stats_cache


@receiver(post_save, sender=UserBook)
@receiver(post_delete, sender=UserBook)
def on_userbook_change(sender, instance, **kwargs):
    invalidate_user_stats_cache(instance.user_id)


@receiver(post_save, sender=ReadingSession)
@receiver(post_delete, sender=ReadingSession)
def on_reading_session_change(sender, instance, **kwargs):
    invalidate_user_stats_cache(instance.user_book.user_id)
