import factory

from apps.books.models import Book
from apps.library.models import UserBook


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Test Book {n}")
    author = "Test Author"
    isbn = factory.Sequence(lambda n: f"978000000{n:04d}")


class UserBookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserBook

    book = factory.SubFactory(BookFactory)
    status = "want_to_read"