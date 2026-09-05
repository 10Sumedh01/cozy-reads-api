from django.contrib import admin

from .models import ReadingGoal


@admin.register(ReadingGoal)
class ReadingGoalAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "target", "year", "month"]
    list_filter = ["type", "year"]
