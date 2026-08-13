from django.urls import path

from .views import RoomTypeViewSet, RoomViewSet

room_type_list = RoomTypeViewSet.as_view({"get": "list", "post": "create"})
room_type_detail = RoomTypeViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)

room_list = RoomViewSet.as_view({"get": "list", "post": "create"})
room_summary = RoomViewSet.as_view({"get": "summary"})
room_detail = RoomViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
)
room_status = RoomViewSet.as_view({"patch": "update_status"})

urlpatterns = [
    path("room-types/", room_type_list, name="room-type-list"),
    path("room-types/<int:pk>/", room_type_detail, name="room-type-detail"),
    path("rooms/", room_list, name="room-list"),
    path("rooms/summary/", room_summary, name="room-summary"),
    path("rooms/<int:pk>/", room_detail, name="room-detail"),
    path("rooms/<int:pk>/status/", room_status, name="room-status"),
]
