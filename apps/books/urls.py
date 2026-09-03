from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BookSearchExternalView, BookViewSet

router = DefaultRouter()
router.register("", BookViewSet, basename="book")

urlpatterns = [
    path("search-external/", BookSearchExternalView.as_view(), name="book-search-external"),
] + router.urls