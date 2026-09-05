from rest_framework import serializers

from .models import GoalTypeChoices, ReadingGoal


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingGoal
        fields = ["id", "type", "target", "year", "month", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        goal_type = attrs.get("type", getattr(self.instance, "type", None))
        month = attrs.get("month", getattr(self.instance, "month", None))

        if goal_type == GoalTypeChoices.MONTHLY_PAGES and not month:
            raise serializers.ValidationError(
                {"month": "Required for monthly_pages goals."}
            )
        if goal_type == GoalTypeChoices.ANNUAL_BOOKS and month:
            raise serializers.ValidationError(
                {"month": "Must be blank for annual_books goals."}
            )
        if month is not None and not (1 <= month <= 12):
            raise serializers.ValidationError({"month": "Must be between 1 and 12."})
        return attrs
