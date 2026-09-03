from rest_framework import permissions, viewsets

from apps.core.permissions import IsOwner

from .models import UserBook
from .serializers import UserBookSerializer


class UserBookViewSet(viewsets.ModelViewSet):
    serializer_class = UserBookSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filterset_fields = ["status", "book_type"]

    def get_queryset(self):
        return UserBook.objects.filter(user=self.request.user).select_related("book")