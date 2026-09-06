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
        cover_url = validated_data.pop("book_cover_url", "") or None
        description = validated_data.pop("book_description", "") or None
        genre = validated_data.pop("book_genre", "") or None
        publisher = validated_data.pop("book_publisher", "") or None
        total_pages = validated_data.pop("book_total_pages", None)

        defaults = {
            "title": title,
            "author": author,
            "cover_url": cover_url,
            "description": description,
            "genre": genre,
            "publisher": publisher,
            "total_pages": total_pages,
        }

        if isbn:
            book, created = Book.objects.get_or_create(isbn=isbn, defaults=defaults)
        else:
            book = Book.objects.create(**defaults)

        user = self.context["request"].user

        if UserBook.objects.filter(user=user, book=book).exists():
            raise serializers.ValidationError(
                {"detail": "This book is already in your library."}
            )

        return UserBook.objects.create(user=user, book=book, **validated_data)


# serializers.py — add this
class UpdateProgressSerializer(serializers.Serializer):
    current_page = serializers.IntegerField(required=False, min_value=0)
    current_position = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if "current_page" not in attrs and "current_position" not in attrs:
            raise serializers.ValidationError(
                "Provide current_page and/or current_position."
            )
        return attrs
