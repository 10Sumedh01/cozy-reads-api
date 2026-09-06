from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.library.models import ReadingSession, StatusChoices, UserBook


class StatsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        finished = UserBook.objects.filter(
            user=request.user, status=StatusChoices.FINISHED
        )

        total_pages = finished.aggregate(total=Sum("book__total_pages"))["total"] or 0

        favourite = (
            finished.exclude(book__genre__isnull=True)
            .values("book__genre")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )

        return Response(
            {
                "books_read": finished.count(),
                "total_pages_read": total_pages,
                "favourite_genre": favourite["book__genre"] if favourite else None,
                "current_streak_days": self._current_streak(finished),
            }
        )

    def _current_streak(self, finished_qs):
        session_dates = set(
            ReadingSession.objects.filter(
                user_book__user=self.request.user
            ).values_list("created_at__date", flat=True)
        )
        streak = 0
        day = timezone.now().date()

        # Grace period: if no session logged yet today but there was one
        # yesterday, don't show the streak as broken until the day actually ends.
        if day not in session_dates and (day - timedelta(days=1)) in session_dates:
            day -= timedelta(days=1)

        while day in session_dates:
            streak += 1
            day -= timedelta(days=1)

        return streak


class StatsByMonthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rows = (
            UserBook.objects.filter(user=request.user, status=StatusChoices.FINISHED)
            .exclude(finished_at__isnull=True)
            .annotate(month=TruncMonth("finished_at"))
            .values("month")
            .annotate(books=Count("id"), pages=Sum("book__total_pages"))
            .order_by("month")
        )
        return Response(
            [
                {
                    "month": r["month"].strftime("%Y-%m"),
                    "books": r["books"],
                    "pages": r["pages"] or 0,
                }
                for r in rows
            ]
        )


class StatsByGenreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rows = (
            UserBook.objects.filter(user=request.user, status=StatusChoices.FINISHED)
            .exclude(book__genre__isnull=True)
            .values("book__genre")
            .annotate(books=Count("id"))
            .order_by("-books")
        )
        return Response(
            [{"genre": r["book__genre"], "books": r["books"]} for r in rows]
        )
