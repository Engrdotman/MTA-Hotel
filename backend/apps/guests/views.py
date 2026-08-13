from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.permissions import CanAccessGuests

from .filters import apply_guest_filters
from .models import Guest
from .serializers import GuestSerializer


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
        return apply_guest_filters(queryset, self.request.query_params)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "This guest cannot be removed because historical records "
                        "depend on the guest."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
