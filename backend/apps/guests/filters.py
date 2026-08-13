from django.db.models import Q


ALLOWED_ORDERING_FIELDS = {"created_at", "first_name", "last_name"}


def apply_guest_filters(queryset, params):
    search = params.get("search", "").strip()
    nationality = params.get("nationality", "").strip()
    id_type = params.get("id_type", "").strip()
    ordering = params.get("ordering", "").strip()

    if search:
        queryset = queryset.filter(
            Q(guest_code__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(phone__icontains=search)
            | Q(email__icontains=search)
            | Q(id_number__icontains=search)
        )

    if nationality:
        queryset = queryset.filter(nationality__iexact=nationality)

    if id_type:
        queryset = queryset.filter(id_type__iexact=id_type)

    if ordering:
        direction = "-" if ordering.startswith("-") else ""
        field = ordering.removeprefix("-")
        if field in ALLOWED_ORDERING_FIELDS:
            queryset = queryset.order_by(f"{direction}{field}", "id")

    return queryset
