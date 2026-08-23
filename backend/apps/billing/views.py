from decimal import Decimal

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.billing.models import Invoice, StayCharge
from apps.billing.serializers import (
    InvoiceListSerializer,
    InvoiceDetailSerializer,
    CreateInvoiceSerializer,
    RecordPaymentSerializer,
    PaymentSerializer,
    StayChargeSerializer,
)
from apps.billing.filters import InvoiceFilter
from apps.billing.permissions import CanAccessBilling, CanManageInvoices, CanRecordPayments
from apps.billing.services import InvoiceService, PaymentService
from apps.stays.models import Stay
from rest_framework.permissions import IsAuthenticated


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for invoice management."""
    
    queryset = Invoice.objects.select_related("guest", "reservation", "stay").prefetch_related("items", "payments")
    permission_classes = (IsAuthenticated, CanAccessBilling)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = InvoiceFilter
    search_fields = ("invoice_number", "guest__first_name", "guest__last_name", "reservation__reservation_number")
    ordering_fields = ("invoice_number", "issued_at", "total", "balance", "created_at")
    ordering = ("-created_at",)
    pagination_class = None  # TODO: Add pagination

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        elif self.action == "create":
            return CreateInvoiceSerializer
        elif self.action == "record_payment":
            return RecordPaymentSerializer
        return InvoiceDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create an invoice for a stay.
        
        POST /api/billing/invoices/
        {
            "stay_id": 1,
            "discount": 0,
            "notes": ""
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            stay_id = serializer.validated_data["stay_id"]
            discount = serializer.validated_data.get("discount")
            notes = serializer.validated_data.get("notes", "")

            # Get stay
            try:
                stay = Stay.objects.select_related("guest", "reservation", "room__room_type").get(id=stay_id)
            except Stay.DoesNotExist:
                return Response(
                    {"error": "Stay not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Check for existing invoice
            existing = Invoice.objects.filter(stay=stay).exclude(status=Invoice.Status.VOID).first()
            if existing:
                return Response(
                    {"error": f"Invoice already exists for this stay: {existing.invoice_number}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create invoice
            with transaction.atomic():
                invoice = InvoiceService.create_invoice_for_stay(
                    stay=stay,
                    discount=discount,
                    created_by=request.user,
                )
                if notes:
                    invoice.notes = notes
                    invoice.save()

            output_serializer = InvoiceDetailSerializer(invoice)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, CanManageInvoices])
    def issue(self, request, pk=None):
        """Issue a draft invoice.
        
        POST /api/billing/invoices/{id}/issue/
        """
        invoice = self.get_object()

        try:
            invoice = InvoiceService.issue_invoice(invoice)
            serializer = InvoiceDetailSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, CanManageInvoices])
    def void(self, request, pk=None):
        """Void an invoice.
        
        POST /api/billing/invoices/{id}/void/
        """
        invoice = self.get_object()

        try:
            invoice = InvoiceService.void_invoice(invoice)
            serializer = InvoiceDetailSerializer(invoice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, CanAccessBilling])
    def payments(self, request, pk=None):
        """Get payment history for an invoice.
        
        GET /api/billing/invoices/{id}/payments/
        """
        invoice = self.get_object()
        payments = invoice.payments.all().order_by("-payment_date")
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, CanRecordPayments])
    def record_payment(self, request, pk=None):
        """Record a payment for an invoice.
        
        POST /api/billing/invoices/{id}/record_payment/
        {
            "amount": 50000,
            "method": "CASH",
            "notes": ""
        }
        """
        invoice = self.get_object()
        serializer = RecordPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            amount = Decimal(str(serializer.validated_data["amount"]))
            method = serializer.validated_data["method"]
            notes = serializer.validated_data.get("notes", "")

            # Record payment
            with transaction.atomic():
                payment = PaymentService.record_payment(
                    invoice=invoice,
                    amount=amount,
                    method=method,
                    received_by=request.user,
                    notes=notes,
                )

            # Refresh invoice
            invoice.refresh_from_db()
            invoice_serializer = InvoiceDetailSerializer(invoice)

            return Response(
                {
                    "payment": PaymentSerializer(payment).data,
                    "invoice": invoice_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StayChargeViewSet(viewsets.ModelViewSet):
    """ViewSet for charges added during a guest stay before invoicing."""

    serializer_class = StayChargeSerializer
    permission_classes = (IsAuthenticated, CanAccessBilling)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ("service_date", "created_at", "amount")
    ordering = ("-service_date", "-created_at")
    pagination_class = None

    def get_queryset(self):
        queryset = StayCharge.objects.select_related("stay__guest", "stay__room", "invoice", "created_by")
        stay_id = self.request.query_params.get("stay")
        status_filter = self.request.query_params.get("status")
        if stay_id:
            queryset = queryset.filter(stay_id=stay_id)
        if status_filter in StayCharge.Status.values:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
