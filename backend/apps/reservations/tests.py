from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
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


class ReservationApiTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="RECEPTIONIST")
        self.user = User.objects.create_user(
            email="reservations@example.com",
            password="StrongPass123",
            first_name="Reservation",
            last_name="Agent",
            role=role,
        )
        self.client.force_authenticate(user=self.user)
        self.room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="25000.00")
        self.room = Room.objects.create(room_number="101", room_type=self.room_type)
        self.second_room = Room.objects.create(room_number="102", room_type=self.room_type)
        self.guest = Guest.objects.create(
            guest_code="GST-000001",
            first_name="Ada",
            last_name="Lovelace",
            phone="08000000000",
        )
        self.second_guest = Guest.objects.create(
            guest_code="GST-000002",
            first_name="Grace",
            last_name="Hopper",
            phone="08000000001",
        )

    def reservation_payload(self, **overrides):
        payload = {
            "guest": self.guest.id,
            "room": self.room.id,
            "check_in_date": "2026-08-20",
            "check_out_date": "2026-08-23",
            "adults": 1,
            "children": 0,
            "status": Reservation.Status.CONFIRMED,
            "source": Reservation.Source.PHONE,
            "special_requests": "Late arrival.",
            "notes": "VIP.",
            "additional_guest_ids": [self.second_guest.id],
        }
        payload.update(overrides)
        return payload

    def create_reservation(self, **overrides):
        payload = self.reservation_payload(**overrides)
        reservation_number = payload.pop("reservation_number", f"RSV-{Reservation.objects.count() + 1:06d}")
        payload["guest"] = Guest.objects.get(pk=payload["guest"])
        payload["room"] = Room.objects.get(pk=payload["room"])
        additional_guest_ids = payload.pop("additional_guest_ids", [])
        reservation = Reservation.objects.create(
            reservation_number=reservation_number,
            created_by=self.user,
            **payload,
        )
        ReservationGuest.objects.create(reservation=reservation, guest=reservation.guest, is_primary=True)
        for guest_id in additional_guest_ids:
            ReservationGuest.objects.create(reservation=reservation, guest_id=guest_id)
        return reservation

    def test_create_reservation_generates_number_and_guest_links(self):
        response = self.client.post(reverse("reservation-list"), self.reservation_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reservation_number"], "RSV-000001")
        self.assertEqual(response.data["guest_name"], "Ada Lovelace")
        self.assertEqual(response.data["room_number"], "101")
        self.assertEqual(response.data["nights"], 3)
        self.assertEqual(len(response.data["additional_guests"]), 1)

    def test_next_reservation_number_uses_padded_sequence(self):
        self.create_reservation(reservation_number="RSV-000009")

        response = self.client.post(
            reverse("reservation-list"),
            self.reservation_payload(room=self.second_room.id, check_in_date="2026-09-01", check_out_date="2026-09-03"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reservation_number"], "RSV-000010")

    def test_checkout_must_be_after_checkin(self):
        response = self.client.post(
            reverse("reservation-list"),
            self.reservation_payload(check_in_date="2026-08-20", check_out_date="2026-08-20"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("check_out_date", response.data)

    def test_active_room_overlap_is_rejected(self):
        self.create_reservation()

        response = self.client.post(
            reverse("reservation-list"),
            self.reservation_payload(check_in_date="2026-08-22", check_out_date="2026-08-24"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("room", response.data)

    def test_cancelled_reservation_does_not_block_room_overlap(self):
        self.create_reservation(status=Reservation.Status.CANCELLED)

        response = self.client.post(
            reverse("reservation-list"),
            self.reservation_payload(check_in_date="2026-08-22", check_out_date="2026-08-24"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_reservation(self):
        reservation = self.create_reservation()

        response = self.client.patch(
            reverse("reservation-detail", kwargs={"pk": reservation.pk}),
            {"room": self.second_room.id, "children": 1, "notes": "Updated"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["room_number"], "102")
        self.assertEqual(response.data["children"], 1)

    def test_moving_reservation_releases_old_room(self):
        reservation = self.create_reservation(status=Reservation.Status.CONFIRMED)

        response = self.client.patch(
            reverse("reservation-detail", kwargs={"pk": reservation.pk}),
            {"room": self.second_room.id},
            format="json",
        )
        self.room.refresh_from_db()
        self.second_room.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.room.status, Room.Status.AVAILABLE)
        self.assertEqual(self.second_room.status, Room.Status.RESERVED)

    def test_update_reservation_status(self):
        reservation = self.create_reservation(status=Reservation.Status.CONFIRMED)

        response = self.client.patch(
            reverse("reservation-status", kwargs={"pk": reservation.pk}),
            {"status": Reservation.Status.CHECKED_IN},
            format="json",
        )
        self.room.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Reservation.Status.CHECKED_IN)
        self.assertEqual(self.room.status, Room.Status.OCCUPIED)

    def test_cancelling_reservation_releases_room(self):
        reservation = self.create_reservation(status=Reservation.Status.CONFIRMED)

        response = self.client.patch(
            reverse("reservation-status", kwargs={"pk": reservation.pk}),
            {"status": Reservation.Status.CANCELLED},
            format="json",
        )
        self.room.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.room.status, Room.Status.AVAILABLE)

    def test_reservation_search_and_filtering(self):
        self.create_reservation(reservation_number="RSV-000001", status=Reservation.Status.CONFIRMED)
        self.create_reservation(
            reservation_number="RSV-000002",
            room=self.second_room.id,
            status=Reservation.Status.PENDING,
            check_in_date="2026-09-01",
            check_out_date="2026-09-04",
        )

        response = self.client.get(
            reverse("reservation-list"),
            {"search": "Ada", "status": Reservation.Status.CONFIRMED, "date_from": "2026-08-19", "date_to": "2026-08-24"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["reservation_number"], "RSV-000001")

    def test_reservation_summary(self):
        self.create_reservation(status=Reservation.Status.CONFIRMED)
        self.create_reservation(
            room=self.second_room.id,
            status=Reservation.Status.PENDING,
            check_in_date="2026-09-01",
            check_out_date="2026-09-04",
        )

        response = self.client.get(reverse("reservation-summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 2)
        self.assertEqual(response.data["confirmed"], 1)
        self.assertEqual(response.data["pending"], 1)

    def test_reservation_pagination(self):
        for index in range(25):
            room = Room.objects.create(room_number=f"{index + 200}", room_type=self.room_type)
            self.create_reservation(
                room=room.id,
                check_in_date=f"2026-09-{index + 1:02d}",
                check_out_date=f"2026-09-{index + 2:02d}",
            )

        response = self.client.get(reverse("reservation-list"), {"page_size": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 10)

    def test_authentication_required(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("reservation-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
