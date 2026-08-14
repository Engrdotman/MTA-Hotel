from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.rooms.models import Room


class Stay(TimeStampedModel):
    class Status(models.TextChoices):
        CHECKED_IN = "CHECKED_IN", "Checked in"
        CHECKED_OUT = "CHECKED_OUT", "Checked out"

    reservation = models.ForeignKey(Reservation, on_delete=models.PROTECT, related_name="stays")
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name="stays")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="stays")
    checked_in_at = models.DateTimeField()
    checked_out_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checked_in_stays",
    )
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checked_out_stays",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CHECKED_IN)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-checked_in_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["reservation"],
                condition=models.Q(status="CHECKED_IN"),
                name="unique_active_stay_per_reservation",
            ),
        ]
        indexes = [
            models.Index(fields=["reservation"], name="stay_reservation_idx"),
            models.Index(fields=["guest"], name="stay_guest_idx"),
            models.Index(fields=["room"], name="stay_room_idx"),
            models.Index(fields=["status"], name="stay_status_idx"),
            models.Index(fields=["checked_in_at"], name="stay_checked_in_idx"),
            models.Index(fields=["checked_out_at"], name="stay_checked_out_idx"),
        ]

    def __str__(self):
        return f"{self.guest} in {self.room}"
