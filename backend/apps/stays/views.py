from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import CanAccessStays

from .models import Stay
from .serializers import CheckInSerializer, CheckOutSerializer, StaySerializer
from .services import build_stay_summary, check_in_reservation, check_out_stay, get_stay_queryset


class StayPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class StayViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StaySerializer
    permission_classes = [IsAuthenticated, CanAccessStays]
    pagination_class = StayPagination

    def get_queryset(self):
        queryset = get_stay_queryset()
        status_filter = self.request.query_params.get("status")
        if status_filter in Stay.Status.values:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        return Response(build_stay_summary(), status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="check-in", url_name="check-in")
    def check_in(self, request):
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stay = check_in_reservation(
            reservation_id=serializer.validated_data["reservation_id"],
            user=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(self.get_serializer(stay).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="check-out", url_name="check-out")
    def check_out(self, request, pk=None):
        serializer = CheckOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        stay = check_out_stay(
            stay=self.get_object(),
            user=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(self.get_serializer(stay).data, status=status.HTTP_200_OK)
