import hashlib
from typing import Union

from django.core.cache import cache

# ---------------------------------------------------------------------------
# Cache TTLs (in seconds)
# ---------------------------------------------------------------------------
TTL_STATS_SUMMARY = 60 * 60  # 1 hour
TTL_STATS_BY_MONTH = 60 * 60  # 1 hour
TTL_STATS_BY_GENRE = 60 * 60  # 1 hour
TTL_GOALS_PROGRESS = 60 * 60  # 1 hour
TTL_GOOGLE_BOOKS_SEARCH = 60 * 60 * 24  # 24 hours
TTL_BOOK_DETAIL = 60 * 60 * 24  # 24 hours


# ---------------------------------------------------------------------------
# Key Generators
# ---------------------------------------------------------------------------
def google_books_search_key(query: str, search_type: str = "title") -> str:
    """Generates an MD5-hashed cache key for Google Books search queries."""
    digest = hashlib.md5(f"{search_type}:{query}".strip().lower().encode()).hexdigest()
    return f"google_books:search:{digest}"


def user_goals_progress_key(user_id: Union[int, str]) -> str:
    """Cache key for user's reading goals progress."""
    return f"user:{user_id}:goals:progress"


def user_stats_summary_key(user_id: Union[int, str]) -> str:
    """Cache key for user's overall reading statistics summary."""
    return f"user:{user_id}:stats:summary"


def user_stats_by_month_key(user_id: Union[int, str]) -> str:
    """Cache key for user's reading statistics grouped by month."""
    return f"user:{user_id}:stats:by-month"


def user_stats_by_genre_key(user_id: Union[int, str]) -> str:
    """Cache key for user's reading statistics grouped by genre."""
    return f"user:{user_id}:stats:by-genre"


def book_detail_key(book_id: Union[int, str]) -> str:
    """Cache key for a specific book catalog entry."""
    return f"book:{book_id}:detail"


# ---------------------------------------------------------------------------
# Invalidation Helpers
# ---------------------------------------------------------------------------
def invalidate_user_goals_cache(user_id: Union[int, str]) -> None:
    """Deletes reading goal progress cache for the given user."""
    cache.delete(user_goals_progress_key(user_id))


def invalidate_user_stats_cache(user_id: Union[int, str]) -> None:
    """
    Deletes all stats and goal progress caches for the given user.
    Called when reading sessions, user books, or book details change.
    """
    keys = [
        user_stats_summary_key(user_id),
        user_stats_by_month_key(user_id),
        user_stats_by_genre_key(user_id),
        user_goals_progress_key(user_id),
    ]
    cache.delete_many(keys)


def invalidate_book_cache(book_id: Union[int, str]) -> None:
    """Deletes cached book details."""
    cache.delete(book_detail_key(book_id))
