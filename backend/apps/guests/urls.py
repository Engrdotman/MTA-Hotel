from django.urls import path

from .views import GuestViewSet

guest_list = GuestViewSet.as_view({"get": "list", "post": "create"})
guest_detail = GuestViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("", guest_list, name="guest-list"),
    path("<int:pk>/", guest_detail, name="guest-detail"),
]
