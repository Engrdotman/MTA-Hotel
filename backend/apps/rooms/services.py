from django.db.models import Count

from .models import Room, RoomType


def get_room_queryset():
    return Room.objects.select_related("room_type")


def get_room_type_queryset():
    return RoomType.objects.annotate(room_count=Count("rooms"))


def build_room_summary():
    counts = dict(Room.objects.values_list("status").annotate(total=Count("id")))

    return {
        "total": Room.objects.count(),
        "available": counts.get(Room.Status.AVAILABLE, 0),
        "occupied": counts.get(Room.Status.OCCUPIED, 0),
        "reserved": counts.get(Room.Status.RESERVED, 0),
    }
