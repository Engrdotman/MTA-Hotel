from django.db.models import Q


ROOM_ORDERING_FIELDS = {"room_number", "floor", "status", "created_at"}
ROOM_TYPE_ORDERING_FIELDS = {"name", "capacity", "base_price", "created_at"}


def apply_room_filters(queryset, params):
    search = params.get("search", "").strip()
    room_type = params.get("room_type", "").strip()
    status = params.get("status", "").strip()
    floor = params.get("floor", "").strip()
    ordering = params.get("ordering", "").strip()

    if search:
        queryset = queryset.filter(room_number__icontains=search)

    if room_type:
        queryset = queryset.filter(room_type_id=room_type)

    if status:
        # Make status filter case-insensitive
        queryset = queryset.filter(status__iexact=status)

    if floor:
        queryset = queryset.filter(floor__iexact=floor)

    return apply_ordering(queryset, ordering, ROOM_ORDERING_FIELDS, "room_number")


def apply_room_type_filters(queryset, params):
    search = params.get("search", "").strip()
    ordering = params.get("ordering", "").strip()

    if search:
        queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

    return apply_ordering(queryset, ordering, ROOM_TYPE_ORDERING_FIELDS, "name")


def apply_ordering(queryset, ordering, allowed_fields, fallback):
    if not ordering:
        return queryset.order_by(fallback, "id")

    direction = "-" if ordering.startswith("-") else ""
    field = ordering.removeprefix("-")

    if field in allowed_fields:
        return queryset.order_by(f"{direction}{field}", "id")

    return queryset.order_by(fallback, "id")
