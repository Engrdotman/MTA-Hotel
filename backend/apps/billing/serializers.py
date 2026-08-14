from rest_framework import serializers

from apps.billing.models import Invoice, InvoiceItem
from apps.payments.models import Payment


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items."""
    
    item_type_display = serializers.CharField(source="get_item_type_display", read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ("id", "item_type", "item_type_display", "description", "quantity", "unit_price", "amount", "service_date")
        read_only_fields = ("id", "amount")


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""
    
    method_display = serializers.CharField(source="get_method_display", read_only=True)
    received_by_email = serializers.CharField(source="received_by.email", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "payment_reference", "amount", "method", "method_display", "payment_date", "received_by_email", "notes", "created_at")
        read_only_fields = ("id", "payment_reference", "created_at")


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer for invoice list view."""
    
    guest_name = serializers.SerializerMethodField()
    reservation_number = serializers.CharField(source="reservation.reservation_number", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id",
            "invoice_number",
            "guest_name",
            "reservation_number",
            "status",
            "status_display",
            "total",
            "amount_paid",
            "balance",
            "issued_at",
            "currency",
        )
        read_only_fields = fields

    def get_guest_name(self, obj):
        return f"{obj.guest.first_name} {obj.guest.last_name}"


class InvoiceDetailSerializer(serializers.ModelSerializer):
    """Serializer for invoice detail view."""
    
    guest_name = serializers.SerializerMethodField()
    guest_code = serializers.CharField(source="guest.guest_code", read_only=True)
    guest_phone = serializers.CharField(source="guest.phone", read_only=True)
    guest_email = serializers.CharField(source="guest.email", read_only=True)
    
    reservation_number = serializers.CharField(source="reservation.reservation_number", read_only=True)
    room_number = serializers.SerializerMethodField()
    room_type = serializers.SerializerMethodField()
    
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id",
            "invoice_number",
            "guest_name",
            "guest_code",
            "guest_phone",
            "guest_email",
            "reservation_number",
            "room_number",
            "room_type",
            "status",
            "status_display",
            "subtotal",
            "discount",
            "tax",
            "total",
            "amount_paid",
            "balance",
            "currency",
            "issued_at",
            "due_at",
            "notes",
            "items",
            "payments",
            "created_by_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_guest_name(self, obj):
        return f"{obj.guest.first_name} {obj.guest.last_name}"
    
    def get_room_number(self, obj):
        return obj.stay.room.room_number if obj.stay else "N/A"
    
    def get_room_type(self, obj):
        return obj.stay.room.room_type.name if obj.stay else "N/A"


class CreateInvoiceSerializer(serializers.Serializer):
    """Serializer for creating an invoice from a stay."""
    
    stay_id = serializers.IntegerField(required=True)
    discount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_discount(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Discount cannot be negative")
        return value


class RecordPaymentSerializer(serializers.Serializer):
    """Serializer for recording a payment."""
    
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    method = serializers.ChoiceField(choices=Payment.Method.choices, required=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


