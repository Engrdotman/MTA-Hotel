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
        OTHER = "OTHER", "Other"

    payment_reference = models.CharField(max_length=50, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Payment amount in NGN")
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    payment_date = models.DateTimeField(null=True, blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_payments",
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["payment_reference"], name="unique_payment_reference"),
            models.CheckConstraint(condition=Q(amount__gt=0), name="payment_amount_gt_0"),
        ]
        indexes = [
            models.Index(fields=["payment_reference"], name="payment_reference_idx"),
            models.Index(fields=["invoice"], name="payment_invoice_idx"),
            models.Index(fields=["payment_date"], name="payment_date_idx"),
        ]

    def __str__(self):
        return self.payment_reference
