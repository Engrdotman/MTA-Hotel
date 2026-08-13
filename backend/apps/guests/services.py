import re

from django.db import IntegrityError, transaction

from .models import Guest


GUEST_CODE_PREFIX = "GST"
GUEST_CODE_WIDTH = 6
MAX_GUEST_CODE_RETRIES = 5


def create_guest(validated_data):
    for _attempt in range(MAX_GUEST_CODE_RETRIES):
        guest_code = generate_next_guest_code()

        try:
            with transaction.atomic():
                return Guest.objects.create(guest_code=guest_code, **validated_data)
        except IntegrityError:
            continue

    raise IntegrityError("Unable to generate a unique guest code.")


def generate_next_guest_code():
    latest_code = (
        Guest.objects.filter(guest_code__regex=rf"^{GUEST_CODE_PREFIX}-[0-9]+$")
        .order_by("-guest_code")
        .values_list("guest_code", flat=True)
        .first()
    )

    next_number = 1
    if latest_code:
        match = re.search(r"(\d+)$", latest_code)
        if match:
            next_number = int(match.group(1)) + 1

    return f"{GUEST_CODE_PREFIX}-{next_number:0{GUEST_CODE_WIDTH}d}"
