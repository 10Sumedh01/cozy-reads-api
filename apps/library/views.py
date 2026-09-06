# flake8:noqa
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import parsers, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsOwner
from apps.epub.tasks import parse_epub_pages

from .models import ReadingSession, UserBook
from .serializers import UpdateProgressSerializer, UserBookSerializer


class UserBookViewSet(viewsets.ModelViewSet):
    serializer_class = UserBookSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ["status", "book_type"]

    def get_queryset(self):
        return UserBook.objects.filter(user=self.request.user).select_related("book")

    @extend_schema(
        summary="Upload an EPUB file for this library entry",
        description=(
            "Accepts a multipart .epub file, saves it immediately, and returns 202. "
            "Page count is calculated asynchronously by a Celery worker — poll "
            "GET /library/{id}/ afterward to see book.total_pages populated."
        ),
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {"file": {"type": "string", "format": "binary"}},
            }
        },
        responses={202: None},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="upload-epub",
        parser_classes=[parsers.MultiPartParser],
    )
    def upload_epub(self, request, pk=None):
        user_book = (
            self.get_object()
        )  # already scoped to this user + runs IsOwner check
        file_obj = request.FILES.get("file")

        if not file_obj:
            return Response({"detail": "No file provided."}, status=400)
        if not file_obj.name.lower().endswith(".epub"):
            return Response({"detail": "Only .epub files are accepted."}, status=400)
        if file_obj.size > 50 * 1024 * 1024:  # 50MB cap
            return Response({"detail": "File too large (max 50MB)."}, status=400)

        user_book.file = file_obj
        user_book.book_type = "epub"
        user_book.save(update_fields=["file", "book_type"])

        parse_epub_pages.delay(user_book.id)

        return Response(
            {
                "detail": "Upload accepted, processing page count.",
                "status": "processing",
            },
            status=202,
        )

    @extend_schema(
        summary="Update reading progress",
        description=(
            "Advances current_page and/or current_position. Logs a "
            "ReadingSession for any positive page increase, and auto-flips "
            "status from want_to_read to reading on first progress update."
        ),
        request=UpdateProgressSerializer,
    )
    @action(detail=True, methods=["patch"], url_path="progress")
    def progress(self, request, pk=None):
        user_book = self.get_object()
        serializer = UpdateProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if "current_page" in data:
            new_page = data["current_page"]
            delta = new_page - user_book.current_page
            if delta > 0:
                ReadingSession.objects.create(user_book=user_book, pages_read=delta)
            user_book.current_page = new_page

        if "current_position" in data:
            user_book.current_position = data["current_position"]

        if user_book.status == "want_to_read":
            user_book.status = "reading"
            user_book.started_at = user_book.started_at or timezone.now().date()

        user_book.save()
        return Response(
            UserBookSerializer(user_book, context={"request": request}).data
        )
