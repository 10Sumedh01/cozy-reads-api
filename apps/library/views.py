# flake8:noqa
from rest_framework import permissions, viewsets

from apps.core.permissions import IsOwner
from drf_spectacular.utils import OpenApiExample, extend_schema
from .models import UserBook
from .serializers import UserBookSerializer
from rest_framework import parsers
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.epub.tasks import parse_epub_pages

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
        request={"multipart/form-data": {"type": "object", "properties": {
            "file": {"type": "string", "format": "binary"}
        }}},
        responses={202: None},
    )
    @action(detail=True, methods=["post"], url_path="upload-epub",parser_classes=[parsers.MultiPartParser])
    def upload_epub(self, request, pk=None):
        user_book = self.get_object()  # already scoped to this user + runs IsOwner check
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
            {"detail": "Upload accepted, processing page count.", "status": "processing"},
            status=202,
        )