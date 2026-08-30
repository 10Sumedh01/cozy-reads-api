from django.db import models


class BaseModel(models.Model):
    """Abstract base providing id, created_at, updated_at for all domain models."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
