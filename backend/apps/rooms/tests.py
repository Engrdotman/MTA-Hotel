from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Room, RoomType


class RoomModelTests(TestCase):
    def test_room_number_is_unique(self):
        room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="100.00")
        Room.objects.create(room_number="101", room_type=room_type)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Room.objects.create(room_number="101", room_type=room_type)

    def test_room_type_rejects_negative_price(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoomType.objects.create(name="Invalid", capacity=1, base_price="-1.00")

    def test_room_type_capacity_must_be_positive(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            RoomType.objects.create(name="Zero", capacity=0, base_price="0.00")
