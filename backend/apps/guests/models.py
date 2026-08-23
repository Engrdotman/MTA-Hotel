from django.db import models

from apps.core.models import TimeStampedModel


class Guest(TimeStampedModel):
    guest_code = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    id_type = models.CharField(max_length=50, blank=True)
    id_number = models.CharField(max_length=80, blank=True)
    nationality = models.CharField(max_length=80, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.UniqueConstraint(fields=["guest_code"], name="unique_guest_code"),
        ]
        indexes = [
            models.Index(fields=["phone"], name="guest_phone_idx"),
            models.Index(fields=["email"], name="guest_email_idx"),
            models.Index(fields=["id_number"], name="guest_id_number_idx"),
            models.Index(fields=["is_active"], name="guest_is_active_idx"),
        ]

    def __str__(self):
        return f"{self.guest_code} - {self.first_name} {self.last_name}"

    def has_historical_records(self):
        related_history = (
            self.primary_reservations,
            self.reservation_links,
            self.stays,
            self.invoices,
        )
        return any(relation.exists() for relation in related_history)
