import re

from django.db import IntegrityError, transaction
from django.db.models import Count, Q

from apps.rooms.models import Room

from .models import Reservation, ReservationGuest


RESERVATION_NUMBER_PREFIX = "RSV"
RESERVATION_NUMBER_WIDTH = 6
MAX_RESERVATION_NUMBER_RETRIES = 5
ACTIVE_RESERVATION_STATUSES = [
    Reservation.Status.PENDING,
    Reservation.Status.CONFIRMED,
    Reservation.Status.CHECKED_IN,
]


def get_reservation_queryset():
    return Reservation.objects.select_related("guest", "room", "room__room_type", "created_by").prefetch_related(
        "reservation_guests__guest"
    )


def create_reservation(validated_data, created_by=None):
    extra_guest_ids = validated_data.pop("additional_guest_ids", [])

    for _attempt in range(MAX_RESERVATION_NUMBER_RETRIES):
        reservation_number = generate_next_reservation_number()

        try:
            with transaction.atomic():
                reservation = Reservation.objects.create(
                    reservation_number=reservation_number,
                    created_by=created_by,
                    **validated_data,
                )
                sync_reservation_guests(reservation, extra_guest_ids)
                update_room_status_for_reservation(reservation)
                return reservation
        except IntegrityError:
            continue

    raise IntegrityError("Unable to generate a unique reservation number.")


def update_reservation(instance, validated_data):
    extra_guest_ids = validated_data.pop("additional_guest_ids", None)

    with transaction.atomic():
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if extra_guest_ids is not None:
            sync_reservation_guests(instance, extra_guest_ids)

        update_room_status_for_reservation(instance)

    return instance


def sync_reservation_guests(reservation, additional_guest_ids):
    ReservationGuest.objects.filter(reservation=reservation).delete()
    ReservationGuest.objects.create(reservation=reservation, guest=reservation.guest, is_primary=True)

    for guest_id in dict.fromkeys(additional_guest_ids):
        if guest_id != reservation.guest_id:
            ReservationGuest.objects.create(reservation=reservation, guest_id=guest_id)


def generate_next_reservation_number():
    latest_number = (
        Reservation.objects.filter(reservation_number__regex=rf"^{RESERVATION_NUMBER_PREFIX}-[0-9]+$")
        .order_by("-reservation_number")
        .values_list("reservation_number", flat=True)
        .first()
    )

    next_number = 1
    if latest_number:
        match = re.search(r"(\d+)$", latest_number)
        if match:
            next_number = int(match.group(1)) + 1

    return f"{RESERVATION_NUMBER_PREFIX}-{next_number:0{RESERVATION_NUMBER_WIDTH}d}"


def has_room_conflict(room, check_in_date, check_out_date, exclude_reservation_id=None):
    queryset = Reservation.objects.filter(
        room=room,
        status__in=ACTIVE_RESERVATION_STATUSES,
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date,
    )

    if exclude_reservation_id:
        queryset = queryset.exclude(pk=exclude_reservation_id)

    return queryset.exists()


def update_room_status_for_reservation(reservation):
    if reservation.status == Reservation.Status.CHECKED_IN:
        reservation.room.status = Room.Status.OCCUPIED
        reservation.room.save(update_fields=["status", "updated_at"])
    elif reservation.status in [Reservation.Status.PENDING, Reservation.Status.CONFIRMED]:
        if reservation.room.status == Room.Status.AVAILABLE:
            reservation.room.status = Room.Status.RESERVED
            reservation.room.save(update_fields=["status", "updated_at"])


def build_reservation_summary():
    counts = dict(Reservation.objects.values_list("status").annotate(total=Count("id")))

    return {
        "total": Reservation.objects.count(),
        "pending": counts.get(Reservation.Status.PENDING, 0),
        "confirmed": counts.get(Reservation.Status.CONFIRMED, 0),
        "checked_in": counts.get(Reservation.Status.CHECKED_IN, 0),
        "cancelled": counts.get(Reservation.Status.CANCELLED, 0),
    }
