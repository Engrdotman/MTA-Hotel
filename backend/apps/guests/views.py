from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.permissions import CanAccessGuests

from .filters import apply_guest_filters
from .models import Guest
from .serializers import GuestSerializer

HISTORICAL_RECORDS_ERROR = "This guest cannot be deleted because historical records exist."


class GuestPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class GuestViewSet(viewsets.ModelViewSet):
    serializer_class = GuestSerializer
    permission_classes = [IsAuthenticated, CanAccessGuests]
    pagination_class = GuestPagination

    def get_queryset(self):
        queryset = Guest.objects.all()
        is_active = self.request.query_params.get("is_active")

        if is_active is None:
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() in ("true", "1", "yes"):
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() in ("false", "0", "no"):
            queryset = queryset.filter(is_active=False)

        return apply_guest_filters(queryset, self.request.query_params)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.has_historical_records():
            return Response(
                {"detail": HISTORICAL_RECORDS_ERROR},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": HISTORICAL_RECORDS_ERROR},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
