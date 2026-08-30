from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "username", "is_staff", "is_active", "created_at"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("mobile", "gender", "profile_pic")}),
    )
