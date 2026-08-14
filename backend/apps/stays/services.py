from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.audit.models import AuditLog
from apps.reservations.models import Reservation
from apps.rooms.models import Room

from .models import Stay


BLOCKED_ROOM_STATUSES = (Room.Status.MAINTENANCE, Room.Status.OUT_OF_SERVICE)
CHECK_IN_ROOM_STATUSES = (Room.Status.AVAILABLE, Room.Status.RESERVED)


def get_stay_queryset():
    return Stay.objects.select_related(
        "reservation",
        "guest",
        "room",
        "room__room_type",
        "checked_in_by",
        "checked_out_by",
    )


def check_in_reservation(*, reservation_id, user, notes=""):
    with transaction.atomic():
        try:
            reservation = Reservation.objects.select_related("guest", "room", "room__room_type").get(pk=reservation_id)
        except Reservation.DoesNotExist as exc:
            raise ValidationError({"reservation_id": "Reservation was not found."}) from exc

        validate_check_in(reservation)

        now = timezone.now()
        stay = Stay.objects.create(
            reservation=reservation,
            guest=reservation.guest,
            room=reservation.room,
            checked_in_at=now,
            checked_in_by=user,
            status=Stay.Status.CHECKED_IN,
            notes=notes or "",
        )

        reservation.status = Reservation.Status.CHECKED_IN
        reservation.save(update_fields=["status", "updated_at"])

        reservation.room.status = Room.Status.OCCUPIED
        reservation.room.save(update_fields=["status", "updated_at"])

        create_stay_audit_log(user=user, action=AuditLog.Action.CHECK_IN, stay=stay)
        return stay


def validate_check_in(reservation):
    if reservation.status != Reservation.Status.CONFIRMED:
        raise ValidationError({"reservation_id": "Only confirmed reservations can be checked in."})

    today = timezone.localdate()
    if today < reservation.check_in_date:
        raise ValidationError({"reservation_id": "Reservation check-in date has not arrived."})
    if today >= reservation.check_out_date:
        raise ValidationError({"reservation_id": "Reservation check-out date has already passed."})

    if reservation.room.status in BLOCKED_ROOM_STATUSES:
        raise ValidationError({"room": "This room cannot be checked in while unavailable."})
    if reservation.room.status not in CHECK_IN_ROOM_STATUSES:
        raise ValidationError({"room": "This room is not available for check-in."})

    if Stay.objects.filter(reservation=reservation, status=Stay.Status.CHECKED_IN).exists():
        raise ValidationError({"reservation_id": "This reservation already has an active stay."})


def check_out_stay(*, stay, user, notes=""):
    with transaction.atomic():
        stay = get_stay_queryset().get(pk=stay.pk)

        if stay.status != Stay.Status.CHECKED_IN:
            raise ValidationError({"stay": "Only checked-in stays can be checked out."})
        if stay.room.status in BLOCKED_ROOM_STATUSES:
            raise ValidationError({"room": "This room status blocks check-out. Resolve room availability first."})
        if stay.room.status != Room.Status.OCCUPIED:
            raise ValidationError({"room": "Only occupied rooms can be checked out."})

        stay.status = Stay.Status.CHECKED_OUT
        stay.checked_out_at = timezone.now()
        stay.checked_out_by = user
        if notes:
            stay.notes = append_note(stay.notes, notes)
        stay.save(update_fields=["status", "checked_out_at", "checked_out_by", "notes", "updated_at"])

        stay.reservation.status = Reservation.Status.CHECKED_OUT
        stay.reservation.save(update_fields=["status", "updated_at"])

        stay.room.status = Room.Status.AVAILABLE
        stay.room.save(update_fields=["status", "updated_at"])

        create_stay_audit_log(user=user, action=AuditLog.Action.CHECK_OUT, stay=stay)
        return stay


def append_note(existing, new_note):
    existing = existing or ""
    new_note = new_note.strip()
    if not existing:
        return new_note
    if not new_note:
        return existing
    return f"{existing}\n\nCheckout: {new_note}"


def create_stay_audit_log(*, user, action, stay):
    AuditLog.objects.create(
        user=user,
        action=action,
        module="stays",
        object_type="Stay",
        object_id=str(stay.pk),
        description=f"{action} for reservation {stay.reservation.reservation_number}",
    )


def build_stay_summary():
    today = timezone.localdate()
    stay_counts = dict(Stay.objects.values_list("status").annotate(total=Count("id")))
    room_counts = dict(Room.objects.values_list("status").annotate(total=Count("id")))

    return {
        "current_guests": stay_counts.get(Stay.Status.CHECKED_IN, 0),
        "today_check_ins": Stay.objects.filter(checked_in_at__date=today).count(),
        "today_check_outs": Stay.objects.filter(checked_out_at__date=today).count(),
        "occupied_rooms": room_counts.get(Room.Status.OCCUPIED, 0),
    }
