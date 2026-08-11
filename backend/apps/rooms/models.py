from django.db import models
from django.db.models import Q

from apps.core.models import TimeStampedModel


class RoomType(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    capacity = models.PositiveSmallIntegerField()
    base_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["name"], name="unique_room_type_name"),
            models.CheckConstraint(condition=Q(capacity__gt=0), name="room_type_capacity_gt_0"),
            models.CheckConstraint(condition=Q(base_price__gte=0), name="room_type_base_price_gte_0"),
        ]

    def __str__(self):
        return self.name


class Room(TimeStampedModel):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        OCCUPIED = "OCCUPIED", "Occupied"
        RESERVED = "RESERVED", "Reserved"
        DIRTY = "DIRTY", "Dirty"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        OUT_OF_SERVICE = "OUT_OF_SERVICE", "Out of service"

    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.PROTECT,
        related_name="rooms",
        help_text="Room types are protected because rooms and historical stays may depend on them.",
    )
    floor = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["room_number"]
        constraints = [
            models.UniqueConstraint(fields=["room_number"], name="unique_room_number"),
        ]
        indexes = [
            models.Index(fields=["room_type"], name="room_room_type_idx"),
            models.Index(fields=["status"], name="room_status_idx"),
        ]

    def __str__(self):
        return f"Room {self.room_number}"
