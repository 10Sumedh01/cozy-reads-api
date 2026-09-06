from django.db.models import Sum
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsOwner
from apps.library.models import ReadingSession, StatusChoices, UserBook

from .models import GoalTypeChoices, ReadingGoal
from .serializers import GoalSerializer


class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ReadingGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Get progress toward all of the user's reading goals",
        responses=OpenApiResponse(
            description="List of goals with computed completion percentage",
        ),
    )
    @action(detail=False, methods=["get"])
    def progress(self, request):
        data = []
        for goal in self.get_queryset():
            if goal.type == GoalTypeChoices.ANNUAL_BOOKS:
                completed = UserBook.objects.filter(
                    user=request.user,
                    status=StatusChoices.FINISHED,
                    finished_at__year=goal.year,
                ).count()
            else:  # monthly_pages
                completed = (
                    ReadingSession.objects.filter(
                        user_book__user=request.user,
                        created_at__year=goal.year,
                        created_at__month=goal.month,
                    ).aggregate(total=Sum("pages_read"))["total"]
                    or 0
                )

            data.append(
                {
                    "id": goal.id,
                    "type": goal.type,
                    "year": goal.year,
                    "month": goal.month,
                    "target": goal.target,
                    "completed": completed,
                    "percent": (
                        round(min(completed / goal.target, 1) * 100, 1)
                        if goal.target
                        else 0
                    ),
                }
            )
        return Response(data)
