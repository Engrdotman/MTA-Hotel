from django.test import TestCase
from django.utils import timezone

from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType
from apps.stays.models import Stay


class StayModelTests(TestCase):
    def test_stay_keeps_actual_times_separate_from_reservation_dates(self):
        room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="100.00")
        room = Room.objects.create(room_number="101", room_type=room_type)
        guest = Guest.objects.create(guest_code="G001", first_name="Ada", last_name="Lovelace")
        reservation = Reservation.objects.create(
            reservation_number="R001",
            guest=guest,
            room=room,
            check_in_date="2026-08-11",
            check_out_date="2026-08-12",
            adults=1,
        )

        stay = Stay.objects.create(
            reservation=reservation,
            guest=guest,
            room=room,
            actual_check_in=timezone.now(),
        )

        self.assertEqual(stay.status, Stay.Status.ACTIVE)
