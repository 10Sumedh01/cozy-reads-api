from django.db import models

from apps.core.models import BaseModel


class Book(BaseModel):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    cover_url = models.URLField(max_length=500, blank=True, null=True)
    total_pages = models.PositiveIntegerField(blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    published_date = models.CharField(max_length=20, blank=True, null=True)
    language = models.CharField(max_length=10, default="en")

    class Meta:
        indexes = [
            models.Index(fields=["isbn"]),
        ]

    def __str__(self):
        return self.title