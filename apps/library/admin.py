from django.contrib import admin

from .models import UserBook


@admin.register(UserBook)
class UserBookAdmin(admin.ModelAdmin):
    list_display = ["user", "book", "status", "current_page", "rating"]
    list_filter = ["status", "book_type"]
