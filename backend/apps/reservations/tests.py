from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.guests.models import Guest
from apps.rooms.models import Room, RoomType

from .models import Reservation, ReservationGuest


class ReservationModelTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="100.00")
        self.room = Room.objects.create(room_number="101", room_type=self.room_type)
        self.guest = Guest.objects.create(guest_code="G001", first_name="Ada", last_name="Lovelace")

    def test_check_out_must_be_after_check_in(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Reservation.objects.create(
                reservation_number="R001",
                guest=self.guest,
                room=self.room,
                check_in_date="2026-08-12",
                check_out_date="2026-08-12",
                adults=1,
            )

    def test_adults_must_be_positive(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Reservation.objects.create(
                reservation_number="R001",
                guest=self.guest,
                room=self.room,
                check_in_date="2026-08-11",
                check_out_date="2026-08-12",
                adults=0,
            )

    def test_duplicate_reservation_guest_is_prevented(self):
        reservation = Reservation.objects.create(
            reservation_number="R001",
            guest=self.guest,
            room=self.room,
            check_in_date="2026-08-11",
            check_out_date="2026-08-12",
            adults=1,
        )
        ReservationGuest.objects.create(reservation=reservation, guest=self.guest, is_primary=True)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ReservationGuest.objects.create(reservation=reservation, guest=self.guest)
