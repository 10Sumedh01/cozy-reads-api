import hashlib
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class GoogleBooksError(Exception):
    """Raised when the Google Books API call fails or returns something we can't use."""


def search_google_books(query, max_results=10, search_type="title"):
    qualifiers = {
        "isbn": f"isbn:{query}",
        "author": f"inauthor:{query}",
        "title": query,
    }
    google_query = qualifiers.get(search_type, query)

    params = {"q": google_query, "maxResults": max_results}
    if settings.GOOGLE_BOOKS_API_KEY:
        params["key"] = settings.GOOGLE_BOOKS_API_KEY

    try:
        response = requests.get(
            f"{settings.GOOGLE_BOOKS_API_BASE_URL}/volumes",
            params=params,
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Google Books request failed: %s", exc, exc_info=True)
        raise GoogleBooksError(str(exc)) from exc

    data = response.json()
    results = []
    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        identifiers = {
            i["type"]: i["identifier"] for i in info.get("industryIdentifiers", [])
        }
        results.append(
            {
                "google_books_id": item.get("id"),
                "title": info.get("title", "Untitled"),
                "author": ", ".join(info.get("authors", [])) or None,
                "isbn": identifiers.get("ISBN_13") or identifiers.get("ISBN_10"),
                "description": info.get("description"),
                "cover_url": info.get("imageLinks", {}).get("thumbnail"),
                "total_pages": info.get("pageCount"),
                "genre": (info.get("categories") or [None])[0],
                "publisher": info.get("publisher"),
                "published_date": info.get("publishedDate"),
                "language": info.get("language", "en"),
            }
        )
    return results


def cache_key_for_query(query, search_type="title"):
    digest = hashlib.md5(f"{search_type}:{query}".strip().lower().encode()).hexdigest()
    return f"google_books:search:{digest}"
