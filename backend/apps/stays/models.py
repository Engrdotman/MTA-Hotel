from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.rooms.models import Room


class Stay(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT, related_name="stays")
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name="stays")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="stays")
    actual_check_in = models.DateTimeField()
    actual_check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_stays",
    )

    class Meta:
        ordering = ["-actual_check_in"]
        indexes = [
            models.Index(fields=["reservation"], name="stay_reservation_idx"),
            models.Index(fields=["guest"], name="stay_guest_idx"),
            models.Index(fields=["room"], name="stay_room_idx"),
            models.Index(fields=["status"], name="stay_status_idx"),
        ]

    def __str__(self):
        return f"{self.guest} in {self.room}"

