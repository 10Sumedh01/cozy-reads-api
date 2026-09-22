from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.cache import TTL_GOOGLE_BOOKS_SEARCH, google_books_search_key

from .models import Book
from .serializers import BookSerializer
from .services import GoogleBooksError, search_google_books


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["genre", "language"]
    search_fields = ["title", "author"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]  # handles create


@extend_schema(
    summary="Search Google Books",
    description=(
        "Proxies a search to the Google Books API, cached in Redis for 24 hours. "
        "Requires authentication — include a valid Bearer access token."
    ),
    parameters=[
        OpenApiParameter("q", str, description="Search query", required=True),
        OpenApiParameter(
            "type",
            str,
            required=False,
            description="What 'q' represents: title (default), author, or isbn.",
        ),
    ],
)
class BookSearchExternalView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "books-search-external"

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        search_type = request.query_params.get("type", "title").strip().lower()

        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if search_type not in {"title", "author", "isbn"}:
            return Response(
                {"detail": "'type' must be one of: title, author, isbn."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache_key = google_books_search_key(query, search_type)
        cached = cache.get(cache_key)
        if cached is not None:
            return Response({"results": cached, "cached": True})

        try:
            results = search_google_books(query, search_type=search_type)
        except GoogleBooksError:
            return Response(
                {
                    "detail": "Google Books is temporarily unavailable. Try again shortly."
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        cache.set(cache_key, results, timeout=TTL_GOOGLE_BOOKS_SEARCH)
        return Response({"results": results, "cached": False})
