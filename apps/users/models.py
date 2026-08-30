from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"

    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(
        max_length=20, choices=GenderChoices.choices, blank=True, null=True
    )
    profile_pic = models.ImageField(
        upload_to="avatars/", default="avatars/default.png", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
