from django.db.models import Q


ALLOWED_ORDERING_FIELDS = {
    "check_in_date",
    "check_out_date",
    "created_at",
    "reservation_number",
    "status",
}


def apply_reservation_filters(queryset, params):
    search = params.get("search", "").strip()
    status = params.get("status", "").strip()
    room = params.get("room", "").strip()
    guest = params.get("guest", "").strip()
    date_from = params.get("date_from", "").strip()
    date_to = params.get("date_to", "").strip()
    ordering = params.get("ordering", "").strip()

    if search:
        queryset = queryset.filter(
            Q(reservation_number__icontains=search)
            | Q(guest__guest_code__icontains=search)
            | Q(guest__first_name__icontains=search)
            | Q(guest__last_name__icontains=search)
            | Q(room__room_number__icontains=search)
        )

    if status:
        queryset = queryset.filter(status=status)

    if room:
        queryset = queryset.filter(room_id=room)

    if guest:
        queryset = queryset.filter(guest_id=guest)

    if date_from:
        queryset = queryset.filter(check_out_date__gt=date_from)

    if date_to:
        queryset = queryset.filter(check_in_date__lt=date_to)

    if ordering:
        direction = "-" if ordering.startswith("-") else ""
        field = ordering.removeprefix("-")
        if field in ALLOWED_ORDERING_FIELDS:
            return queryset.order_by(f"{direction}{field}", "id")

    return queryset
