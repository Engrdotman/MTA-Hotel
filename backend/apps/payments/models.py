from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.billing.models import Invoice
from apps.core.models import TimeStampedModel


class Payment(TimeStampedModel):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        POS = "POS", "POS"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank transfer"
        CARD = "CARD", "Card"
        ONLINE = "ONLINE", "Online"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"
        CANCELLED = "CANCELLED", "Cancelled"

    payment_reference = models.CharField(max_length=50, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_payments",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-paid_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["payment_reference"], name="unique_payment_reference"),
            models.CheckConstraint(condition=Q(amount__gt=0), name="payment_amount_gt_0"),
        ]
        indexes = [
            models.Index(fields=["invoice"], name="payment_invoice_idx"),
            models.Index(fields=["transaction_reference"], name="payment_transaction_ref_idx"),
            models.Index(fields=["status"], name="payment_status_idx"),
            models.Index(fields=["paid_at"], name="payment_paid_at_idx"),
        ]

    def __str__(self):
        return self.payment_reference
