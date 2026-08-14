from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.core.models import TimeStampedModel
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.stays.models import Stay


class Invoice(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ISSUED = "ISSUED", "Issued"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
        PAID = "PAID", "Paid"
        VOID = "VOID", "Void"

    invoice_number = models.CharField(max_length=40, unique=True)
    stay = models.OneToOneField(Stay, on_delete=models.PROTECT, related_name="invoice", null=True, blank=True)
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name="invoices")
    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT, related_name="invoices")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Invoice-level discount in NGN")
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="NGN")
    issued_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_invoices",
    )

    class Meta:
        ordering = ["-issued_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["invoice_number"], name="unique_invoice_number"),
            models.CheckConstraint(condition=Q(subtotal__gte=0), name="invoice_subtotal_gte_0"),
            models.CheckConstraint(condition=Q(discount__gte=0), name="invoice_discount_gte_0"),
            models.CheckConstraint(condition=Q(tax__gte=0), name="invoice_tax_gte_0"),
            models.CheckConstraint(condition=Q(total__gte=0), name="invoice_total_gte_0"),
            models.CheckConstraint(condition=Q(amount_paid__gte=0), name="invoice_amount_paid_gte_0"),
            models.CheckConstraint(condition=Q(balance__gte=0), name="invoice_balance_gte_0"),
        ]
        indexes = [
            models.Index(fields=["invoice_number"], name="invoice_number_idx"),
            models.Index(fields=["guest"], name="invoice_guest_idx"),
            models.Index(fields=["reservation"], name="invoice_reservation_idx"),
            models.Index(fields=["stay"], name="invoice_stay_idx"),
            models.Index(fields=["status"], name="invoice_status_idx"),
            models.Index(fields=["issued_at"], name="invoice_issued_at_idx"),
        ]

    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    class ItemType(models.TextChoices):
        ROOM = "ROOM", "Room"
        SERVICE = "SERVICE", "Service"
        OTHER = "OTHER", "Other"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=20, choices=ItemType.choices, default=ItemType.ROOM)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price per unit in NGN")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total amount (quantity × unit_price) in NGN")
    service_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["service_date", "id"]
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gt=0), name="invoice_item_quantity_gt_0"),
            models.CheckConstraint(condition=Q(unit_price__gte=0), name="invoice_item_unit_price_gte_0"),
            models.CheckConstraint(condition=Q(amount__gte=0), name="invoice_item_amount_gte_0"),
        ]
        indexes = [
            models.Index(fields=["invoice"], name="invoice_item_invoice_idx"),
            models.Index(fields=["item_type"], name="invoice_item_type_idx"),
            models.Index(fields=["service_date"], name="invoice_item_service_date_idx"),
        ]

    def __str__(self):
        return f"{self.invoice} - {self.description}"
