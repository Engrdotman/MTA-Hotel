from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Guest


class GuestModelTests(TestCase):
    def test_guest_code_is_unique(self):
        Guest.objects.create(guest_code="G001", first_name="Ada", last_name="Lovelace")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Guest.objects.create(guest_code="G001", first_name="Grace", last_name="Hopper")
