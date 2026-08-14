from rest_framework.routers import DefaultRouter

from .views import StayViewSet


router = DefaultRouter()
router.register("stays", StayViewSet, basename="stay")

urlpatterns = router.urls
