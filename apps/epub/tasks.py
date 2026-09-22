from celery import shared_task
from ebooklib import epub


@shared_task(bind=True, max_retries=2)
def parse_epub_pages(self, user_book_id):
    from apps.library.models import UserBook

    try:
        user_book = UserBook.objects.get(id=user_book_id)
    except UserBook.DoesNotExist:
        return

    try:
        book = epub.read_epub(user_book.file.path)
        word_count = 0
        for item in book.get_items_of_type(9):  # 9 = ITEM_DOCUMENT (readable content)
            word_count += len(item.get_content().split())
        estimated_pages = max(
            1, word_count // 250
        )  # ~250 words/page, a common estimate
    except Exception as exc:
        # A corrupt/malformed EPUB shouldn't crash the worker or retry forever.
        raise self.retry(exc=exc, countdown=10)

    user_book.book.total_pages = estimated_pages
    user_book.book.save(update_fields=["total_pages"])

    # Invalidate stats for all users who have this book in their library
    from apps.core.cache import invalidate_user_stats_cache

    affected_user_ids = set(
        UserBook.objects.filter(book_id=user_book.book_id).values_list(
            "user_id", flat=True
        )
    )
    for uid in affected_user_ids:
        invalidate_user_stats_cache(uid)
