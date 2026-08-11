from django.conf import settings
from django.db import models
from django.db.models import F, Q

from apps.core.models import TimeStampedModel
from apps.guests.models import Guest
from apps.rooms.models import Room


class Reservation(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CHECKED_IN = "CHECKED_IN", "Checked in"
        CHECKED_OUT = "CHECKED_OUT", "Checked out"
        CANCELLED = "CANCELLED", "Cancelled"
        NO_SHOW = "NO_SHOW", "No show"

    class Source(models.TextChoices):
        WALK_IN = "WALK_IN", "Walk in"
        PHONE = "PHONE", "Phone"
        EMAIL = "EMAIL", "Email"
        WEBSITE = "WEBSITE", "Website"
        AGENT = "AGENT", "Agent"
        OTHER = "OTHER", "Other"

    reservation_number = models.CharField(max_length=40, unique=True)
    guest = models.ForeignKey(
        Guest,
        on_delete=models.PROTECT,
        related_name="primary_reservations",
        help_text="Primary guest for MVP compatibility; additional guests use ReservationGuest.",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name="reservations",
        help_text="Room references are protected to preserve reservation history.",
    )
    guests = models.ManyToManyField(Guest, through="ReservationGuest", related_name="reservations")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    adults = models.PositiveSmallIntegerField(default=1)
    children = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.WALK_IN)
    special_requests = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_reservations",
    )

    class Meta:
        ordering = ["-check_in_date", "reservation_number"]
        constraints = [
            models.UniqueConstraint(fields=["reservation_number"], name="unique_reservation_number"),
            models.CheckConstraint(condition=Q(check_out_date__gt=F("check_in_date")), name="reservation_checkout_after_checkin"),
            models.CheckConstraint(condition=Q(adults__gt=0), name="reservation_adults_gt_0"),
            models.CheckConstraint(condition=Q(children__gte=0), name="reservation_children_gte_0"),
        ]
        indexes = [
            models.Index(fields=["guest"], name="reservation_guest_idx"),
            models.Index(fields=["room"], name="reservation_room_idx"),
            models.Index(fields=["status"], name="reservation_status_idx"),
            models.Index(fields=["check_in_date"], name="reservation_checkin_idx"),
            models.Index(fields=["check_out_date"], name="reservation_checkout_idx"),
            models.Index(fields=["room", "check_in_date", "check_out_date"], name="reservation_room_dates_idx"),
        ]

    def __str__(self):
        return self.reservation_number


class ReservationGuest(models.Model):
    """Links guests to reservations while keeping Reservation.guest as the MVP primary guest pointer."""

    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name="reservation_guests")
    guest = models.ForeignKey(Guest, on_delete=models.PROTECT, related_name="reservation_links")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "created_at"]
        constraints = [
            models.UniqueConstraint(fields=["reservation", "guest"], name="unique_reservation_guest"),
        ]
        indexes = [
            models.Index(fields=["reservation"], name="res_guest_reservation_idx"),
            models.Index(fields=["guest"], name="res_guest_guest_idx"),
        ]

    def __str__(self):
        return f"{self.reservation} - {self.guest}"
