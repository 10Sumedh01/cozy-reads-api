from django.db import models

from apps.core.models import BaseModel


class GoalTypeChoices(models.TextChoices):
    ANNUAL_BOOKS = "annual_books", "Annual Books"
    MONTHLY_PAGES = "monthly_pages", "Monthly Pages"


class ReadingGoal(BaseModel):
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="goals"
    )
    type = models.CharField(max_length=20, choices=GoalTypeChoices.choices)
    target = models.PositiveIntegerField()
    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ("user", "type", "year", "month")

    def __str__(self):
        return f"{self.user} — {self.type} {self.year}"