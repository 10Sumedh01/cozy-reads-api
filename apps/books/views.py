from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book
from .serializers import BookSerializer
from .services import (GoogleBooksError, cache_key_for_query,
                       search_google_books)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["genre", "language"]
    search_fields = ["title", "author"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


@extend_schema(
    summary="Search Google Books",
    description="Proxies a search to the Google Books API, cached in Redis for 24 hours.",
    parameters=[OpenApiParameter("q", str, description="Search query", required=True)],
)
class BookSearchExternalView(APIView):
    permission_classes = [permissions.IsAuthenticated()]
    throttle_scope = "books-search-external"

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = cache_key_for_query(query)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response({"results": cached, "cached": True})

        try:
            results = search_google_books(query)
        except GoogleBooksError:
            return Response(
                {
                    "detail": "Google Books is temporarily unavailable. Try again shortly."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(
            cache_key, results, timeout=60 * 60 * 24
        )  # 24h, per your caching strategy doc
        return Response({"results": results, "cached": False})
