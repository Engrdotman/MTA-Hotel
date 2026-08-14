from datetime import timedelta
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType
from apps.stays.services import check_in_reservation

from .models import Stay


PASSWORD = "StrongPass123!"


class StayModelTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="100.00")
        self.room = Room.objects.create(room_number="101", room_type=self.room_type)
        self.guest = Guest.objects.create(guest_code="G001", first_name="Ada", last_name="Lovelace")
        today = timezone.localdate()
        self.reservation = Reservation.objects.create(
            reservation_number="RSV-000001",
            guest=self.guest,
            room=self.room,
            check_in_date=today,
            check_out_date=today + timedelta(days=2),
            adults=1,
            status=Reservation.Status.CONFIRMED,
        )

    def test_stay_keeps_actual_times_separate_from_reservation_dates(self):
        stay = Stay.objects.create(
            reservation=self.reservation,
            guest=self.guest,
            room=self.room,
            checked_in_at=timezone.now(),
        )

        self.assertEqual(stay.status, Stay.Status.CHECKED_IN)

    def test_duplicate_active_stay_is_prevented_by_database(self):
        Stay.objects.create(
            reservation=self.reservation,
            guest=self.guest,
            room=self.room,
            checked_in_at=timezone.now(),
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Stay.objects.create(
                reservation=self.reservation,
                guest=self.guest,
                room=self.room,
                checked_in_at=timezone.now(),
            )

    def test_completed_stay_history_is_preserved(self):
        Stay.objects.create(
            reservation=self.reservation,
            guest=self.guest,
            room=self.room,
            checked_in_at=timezone.now() - timedelta(days=2),
            checked_out_at=timezone.now() - timedelta(days=1),
            status=Stay.Status.CHECKED_OUT,
        )
        active = Stay.objects.create(
            reservation=self.reservation,
            guest=self.guest,
            room=self.room,
            checked_in_at=timezone.now(),
        )

        self.assertEqual(active.status, Stay.Status.CHECKED_IN)
        self.assertEqual(Stay.objects.filter(reservation=self.reservation).count(), 2)


class StayApiTests(APITestCase):
    def setUp(self):
        self.roles = {name: Role.objects.create(name=name) for name in Role.MVP_ROLES}
        self.users = {
            name: User.objects.create_user(
                email=f"{name.lower()}@example.com",
                password=PASSWORD,
                first_name=name.title(),
                last_name="User",
                role=role,
            )
            for name, role in self.roles.items()
        }
        self.room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="25000.00")
        self.guest_counter = 0
        self.room_counter = 100
        self.reservation_counter = 0

    def authenticate_role(self, role):
        self.client.force_authenticate(user=self.users[role])

    def make_reservation(self, *, status_value=Reservation.Status.CONFIRMED, room_status=Room.Status.AVAILABLE):
        self.guest_counter += 1
        self.room_counter += 1
        self.reservation_counter += 1
        today = timezone.localdate()
        guest = Guest.objects.create(
            guest_code=f"GST-{self.guest_counter:06d}",
            first_name="Ada",
            last_name=f"Guest{self.guest_counter}",
            phone="08000000000",
        )
        room = Room.objects.create(
            room_number=str(self.room_counter),
            room_type=self.room_type,
            status=room_status,
        )
        reservation = Reservation.objects.create(
            reservation_number=f"RSV-{self.reservation_counter:06d}",
            guest=guest,
            room=room,
            check_in_date=today,
            check_out_date=today + timedelta(days=2),
            adults=1,
            status=status_value,
            created_by=self.users[Role.RECEPTIONIST],
        )
        return reservation

    def post_check_in(self, reservation):
        return self.client.post(
            reverse("stay-check-in"),
            {"reservation_id": reservation.id, "notes": "Guest arrived with valid identification."},
            format="json",
        )

    def test_admin_manager_and_receptionist_can_check_in(self):
        for role in (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST):
            self.authenticate_role(role)
            reservation = self.make_reservation()
            response = self.post_check_in(reservation)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, role)
            self.assertEqual(response.data["status"], Stay.Status.CHECKED_IN)

    def test_accountant_and_staff_cannot_check_in(self):
        for role in (Role.ACCOUNTANT, Role.STAFF):
            self.authenticate_role(role)
            response = self.post_check_in(self.make_reservation())
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, role)

    def test_confirmed_reservation_can_check_in_and_updates_state(self):
        self.authenticate_role(Role.RECEPTIONIST)
        reservation = self.make_reservation()

        response = self.post_check_in(reservation)
        reservation.refresh_from_db()
        reservation.room.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reservation.status, Reservation.Status.CHECKED_IN)
        self.assertEqual(reservation.room.status, Room.Status.OCCUPIED)
        self.assertEqual(Stay.objects.filter(reservation=reservation, status=Stay.Status.CHECKED_IN).count(), 1)
        self.assertEqual(Stay.objects.get(reservation=reservation).checked_in_by, self.users[Role.RECEPTIONIST])

    def test_pending_cancelled_checked_in_and_checked_out_reservations_cannot_check_in(self):
        self.authenticate_role(Role.RECEPTIONIST)
        for reservation_status in (
            Reservation.Status.PENDING,
            Reservation.Status.CANCELLED,
            Reservation.Status.CHECKED_IN,
            Reservation.Status.CHECKED_OUT,
        ):
            response = self.post_check_in(self.make_reservation(status_value=reservation_status))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, reservation_status)

    def test_maintenance_and_out_of_service_rooms_cannot_check_in(self):
        self.authenticate_role(Role.RECEPTIONIST)
        for room_status in (Room.Status.MAINTENANCE, Room.Status.OUT_OF_SERVICE):
            response = self.post_check_in(self.make_reservation(room_status=room_status))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, room_status)

    def test_duplicate_active_stay_is_prevented(self):
        self.authenticate_role(Role.RECEPTIONIST)
        reservation = self.make_reservation()
        self.post_check_in(reservation)

        response = self.post_check_in(reservation)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Stay.objects.filter(reservation=reservation, status=Stay.Status.CHECKED_IN).count(), 1)

    def test_successful_checkout_updates_stay_reservation_and_room(self):
        self.authenticate_role(Role.RECEPTIONIST)
        reservation = self.make_reservation()
        check_in_response = self.post_check_in(reservation)
        stay_id = check_in_response.data["id"]

        response = self.client.post(
            reverse("stay-check-out", kwargs={"pk": stay_id}),
            {"notes": "Guest checked out normally."},
            format="json",
        )
        stay = Stay.objects.get(pk=stay_id)
        reservation.refresh_from_db()
        reservation.room.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(stay.status, Stay.Status.CHECKED_OUT)
        self.assertIsNotNone(stay.checked_out_at)
        self.assertEqual(stay.checked_out_by, self.users[Role.RECEPTIONIST])
        self.assertEqual(reservation.status, Reservation.Status.CHECKED_OUT)
        self.assertEqual(reservation.room.status, Room.Status.AVAILABLE)

    def test_already_checked_out_stay_cannot_check_out_again(self):
        self.authenticate_role(Role.RECEPTIONIST)
        reservation = self.make_reservation()
        stay_id = self.post_check_in(reservation).data["id"]
        self.client.post(reverse("stay-check-out", kwargs={"pk": stay_id}), {}, format="json")

        response = self.client.post(reverse("stay-check-out", kwargs={"pk": stay_id}), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_users_receive_401(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("stay-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_users_receive_403_for_checkout(self):
        self.authenticate_role(Role.RECEPTIONIST)
        reservation = self.make_reservation()
        stay_id = self.post_check_in(reservation).data["id"]

        self.authenticate_role(Role.ACCOUNTANT)
        response = self.client.post(reverse("stay-check-out", kwargs={"pk": stay_id}), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_transaction_rollback_when_room_update_fails(self):
        reservation = self.make_reservation()

        with self.assertRaises(RuntimeError):
            with patch.object(Room, "save", side_effect=RuntimeError("room update failed")):
                check_in_reservation(
                    reservation_id=reservation.id,
                    user=self.users[Role.RECEPTIONIST],
                    notes="Rollback test.",
                )

        reservation.refresh_from_db()
        reservation.room.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.CONFIRMED)
        self.assertEqual(reservation.room.status, Room.Status.AVAILABLE)
        self.assertFalse(Stay.objects.filter(reservation=reservation).exists())
