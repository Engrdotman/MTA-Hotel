from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.permissions import CanAccessReservations

from .filters import apply_reservation_filters
from .serializers import ReservationSerializer, ReservationStatusSerializer
from .services import build_reservation_summary, get_reservation_queryset, update_room_status_for_reservation


class ReservationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, CanAccessReservations]
    pagination_class = ReservationPagination

    def get_queryset(self):
        return apply_reservation_filters(get_reservation_queryset(), self.request.query_params)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        return Response(build_reservation_summary(), status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="status", url_name="status")
    def update_status(self, request, pk=None):
        reservation = self.get_object()
        serializer = ReservationStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation.status = serializer.validated_data["status"]
        reservation.save(update_fields=["status", "updated_at"])
        update_room_status_for_reservation(reservation)

        return Response(self.get_serializer(reservation).data, status=status.HTTP_200_OK)
