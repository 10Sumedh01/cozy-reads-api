from django.db import models

from apps.core.models import BaseModel


class StatusChoices(models.TextChoices):
    WANT_TO_READ = "want_to_read", "Want to Read"
    READING = "reading", "Reading"
    FINISHED = "finished", "Finished"


class BookTypeChoices(models.TextChoices):
    PHYSICAL = "physical", "Physical"
    EPUB = "epub", "EPUB"


class UserBook(BaseModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="library"
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.PROTECT, related_name="user_entries"
    )
    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.WANT_TO_READ
    )
    book_type = models.CharField(
        max_length=20, choices=BookTypeChoices.choices, default=BookTypeChoices.PHYSICAL
    )
    current_page = models.PositiveIntegerField(default=0)
    current_position = models.CharField(max_length=500, blank=True, null=True)
    file = models.FileField(upload_to="epubs/%Y/%m/", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(blank=True, null=True)
    personal_notes = models.TextField(blank=True, null=True)
    started_at = models.DateField(blank=True, null=True)
    finished_at = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "book")
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.book}"
