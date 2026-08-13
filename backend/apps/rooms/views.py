from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.permissions import CanAccessRooms

from .filters import apply_room_filters, apply_room_type_filters
from .serializers import RoomSerializer, RoomStatusSerializer, RoomTypeSerializer
from .services import build_room_summary, get_room_queryset, get_room_type_queryset


class RoomsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class RoomTypeViewSet(viewsets.ModelViewSet):
    serializer_class = RoomTypeSerializer
    permission_classes = [IsAuthenticated, CanAccessRooms]
    pagination_class = RoomsPagination

    def get_queryset(self):
        return apply_room_type_filters(get_room_type_queryset(), self.request.query_params)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.rooms.exists():
            return Response(
                {
                    "detail": (
                        "This room type cannot be deleted because rooms are currently "
                        "assigned to it."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "This room type cannot be deleted because rooms are currently "
                        "assigned to it."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated, CanAccessRooms]
    pagination_class = RoomsPagination

    def get_queryset(self):
        return apply_room_filters(get_room_queryset(), self.request.query_params)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        return Response(build_room_summary(), status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        room = self.get_object()
        serializer = RoomStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room.status = serializer.validated_data["status"]
        room.save(update_fields=["status", "updated_at"])

        return Response(self.get_serializer(room).data, status=status.HTTP_200_OK)
