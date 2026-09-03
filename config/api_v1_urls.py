"""
Aggregates all app-level routers under /api/v1/.
Each app's urls.py is added here as it's built (Phase 2+).
"""
from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.users.urls")),
    path("books/", include("apps.books.urls")),        # Phase 3
    path("library/", include("apps.library.urls")),    # Phase 3
    # path("goals/", include("apps.goals.urls")),        # Phase 4
    # path("stats/", include("apps.stats.urls")),        # Phase 4
]
