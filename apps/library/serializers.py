from rest_framework import serializers

from apps.books.models import Book
from apps.books.serializers import BookSerializer

from .models import UserBook


class UserBookSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_isbn = serializers.CharField(write_only=True, required=False, allow_blank=True)
    book_title = serializers.CharField(write_only=True, required=False)
    book_author = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = UserBook
        fields = [
            "id",
            "book",
            "book_isbn",
            "book_title",
            "book_author",
            "status",
            "book_type",
            "current_page",
            "current_position",
            "rating",
            "personal_notes",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if (
            self.instance is None
            and not attrs.get("book_title")
            and not attrs.get("book_isbn")
        ):
            raise serializers.ValidationError(
                "Provide at least book_title to add a book to your library."
            )
        return attrs

    def create(self, validated_data):
        isbn = validated_data.pop("book_isbn", "") or None
        title = validated_data.pop("book_title", "Untitled")
        author = validated_data.pop("book_author", "")

        if isbn:
            book, _ = Book.objects.get_or_create(
                isbn=isbn, defaults={"title": title, "author": author}
            )
        else:
            book = Book.objects.create(title=title, author=author)

        user = self.context["request"].user
        return UserBook.objects.create(user=user, book=book, **validated_data)
