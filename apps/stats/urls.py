from django.urls import path

from .views import StatsByGenreView, StatsByMonthView, StatsSummaryView

urlpatterns = [
    path("summary/", StatsSummaryView.as_view(), name="stats-summary"),
    path("by-month/", StatsByMonthView.as_view(), name="stats-by-month"),
    path("by-genre/", StatsByGenreView.as_view(), name="stats-by-genre"),
]
