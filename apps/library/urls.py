from rest_framework.routers import DefaultRouter

from .views import UserBookViewSet

router = DefaultRouter()
router.register("", UserBookViewSet, basename="userbook")

urlpatterns = router.urls
