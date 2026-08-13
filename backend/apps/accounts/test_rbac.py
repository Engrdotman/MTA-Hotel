from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Role, User
from apps.guests.models import Guest
from apps.reservations.models import Reservation
from apps.rooms.models import Room, RoomType


PASSWORD = "StrongPass123!"


class RoleTestMixin:
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

    def authenticate_role(self, role):
        self.client.force_authenticate(user=self.users[role])


class UserManagementRBACTests(RoleTestMixin, APITestCase):
    def test_only_admin_can_list_users(self):
        for role in Role.MVP_ROLES:
            self.authenticate_role(role)
            response = self.client.get(reverse("user-list"))
            expected = status.HTTP_200_OK if role == Role.ADMIN else status.HTTP_403_FORBIDDEN
            self.assertEqual(response.status_code, expected, role)

    def test_only_admin_can_create_staff_users(self):
        payload = {
            "email": "new.manager@example.com",
            "first_name": "New",
            "last_name": "Manager",
            "phone": "+2348000000002",
            "role": Role.MANAGER,
            "temporary_password": PASSWORD,
            "confirm_password": PASSWORD,
            "is_active": True,
        }

        for role in (Role.MANAGER, Role.RECEPTIONIST, Role.ACCOUNTANT, Role.STAFF):
            self.authenticate_role(role)
            response = self.client.post(reverse("user-list"), payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, role)

        self.authenticate_role(Role.ADMIN)
        response = self.client.post(reverse("user-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], Role.MANAGER)
        self.assertFalse(User.objects.get(email="new.manager@example.com").is_superuser)

    def test_admin_cannot_create_admin_from_staff_creation_endpoint(self):
        self.authenticate_role(Role.ADMIN)
        response = self.client.post(
            reverse("user-list"),
            {
                "email": "second.admin@example.com",
                "first_name": "Second",
                "last_name": "Admin",
                "role": Role.ADMIN,
                "temporary_password": PASSWORD,
                "confirm_password": PASSWORD,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email="second.admin@example.com").exists())

    def test_delete_deactivates_user(self):
        self.authenticate_role(Role.ADMIN)
        target = self.users[Role.STAFF]

        response = self.client.delete(reverse("user-detail", kwargs={"pk": target.pk}))
        target.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(target.is_active)
        self.assertTrue(User.objects.filter(pk=target.pk).exists())

    def test_normal_user_cannot_change_own_role(self):
        receptionist = self.users[Role.RECEPTIONIST]
        self.authenticate_role(Role.RECEPTIONIST)

        response = self.client.patch(
            reverse("user-detail", kwargs={"pk": receptionist.pk}),
            {"role": Role.MANAGER},
            format="json",
        )
        receptionist.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(receptionist.role.name, Role.RECEPTIONIST)


class AuthenticationRBACTests(RoleTestMixin, APITestCase):
    def test_login_me_refresh_and_logout_flow(self):
        login_response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@example.com", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        me_response = self.client.get(reverse("auth-me"))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["role"], Role.ADMIN)
        self.assertNotIn("password", me_response.data)

        refresh_response = self.client.post(
            reverse("auth-token-refresh"),
            {"refresh": login_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)
        current_refresh = refresh_response.data.get("refresh", login_response.data["refresh"])

        logout_response = self.client.post(
            reverse("auth-logout"),
            {"refresh": current_refresh},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_incorrect_password_and_inactive_users_are_rejected(self):
        wrong_password_response = self.client.post(
            reverse("auth-login"),
            {"email": "manager@example.com", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(wrong_password_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.users[Role.STAFF].is_active = False
        self.users[Role.STAFF].save(update_fields=["is_active"])
        inactive_response = self.client.post(
            reverse("auth-login"),
            {"email": "staff@example.com", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(inactive_response.status_code, status.HTTP_401_UNAUTHORIZED)


class HotelModuleRBACTests(RoleTestMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.room_type = RoomType.objects.create(name="Standard", capacity=2, base_price="25000.00")
        self.room = Room.objects.create(room_number="101", room_type=self.room_type)
        self.guest = Guest.objects.create(guest_code="GST-000001", first_name="Ada", last_name="Lovelace")
        self.reservation = Reservation.objects.create(
            reservation_number="RSV-000001",
            guest=self.guest,
            room=self.room,
            check_in_date="2026-08-20",
            check_out_date="2026-08-22",
            adults=1,
            created_by=self.users[Role.RECEPTIONIST],
        )

    def test_guest_role_permissions(self):
        for role in (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST, Role.ACCOUNTANT, Role.STAFF):
            self.authenticate_role(role)
            response = self.client.get(reverse("guest-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK, role)

        for role in (Role.ACCOUNTANT, Role.STAFF):
            self.authenticate_role(role)
            response = self.client.post(reverse("guest-list"), {"first_name": "Nope"}, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, role)

    def test_room_role_permissions(self):
        for role in (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST, Role.STAFF):
            self.authenticate_role(role)
            response = self.client.get(reverse("room-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK, role)

        self.authenticate_role(Role.ACCOUNTANT)
        self.assertEqual(self.client.get(reverse("room-list")).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.client.post(reverse("room-list"), {"room_number": "202"}, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_reservation_role_permissions(self):
        for role in (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST, Role.ACCOUNTANT):
            self.authenticate_role(role)
            response = self.client.get(reverse("reservation-list"))
            self.assertEqual(response.status_code, status.HTTP_200_OK, role)

        for role in (Role.ACCOUNTANT, Role.STAFF):
            self.authenticate_role(role)
            response = self.client.post(reverse("reservation-list"), {}, format="json")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, role)


class CreateAdminCommandTests(APITestCase):
    def test_create_admin_command_creates_application_admin(self):
        out = StringIO()

        with patch("builtins.input", side_effect=["admin@example.com", "Hazzan", "Admin"]):
            with patch("getpass.getpass", side_effect=[PASSWORD, PASSWORD]):
                call_command("create_admin", stdout=out)

        user = User.objects.get(email="admin@example.com")
        self.assertEqual(user.role.name, Role.ADMIN)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

        login_response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@example.com", "password": PASSWORD},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=user)
        self.assertEqual(self.client.get(reverse("user-list")).status_code, status.HTTP_200_OK)
        create_response = self.client.post(
            reverse("user-list"),
            {
                "email": "staff@example.com",
                "first_name": "Staff",
                "last_name": "Member",
                "role": Role.STAFF,
                "temporary_password": PASSWORD,
                "confirm_password": PASSWORD,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

    def test_create_admin_command_rejects_duplicate_email(self):
        role = Role.objects.create(name=Role.ADMIN)
        User.objects.create_user(
            email="admin@example.com",
            password=PASSWORD,
            first_name="Existing",
            last_name="Admin",
            role=role,
        )

        with patch("builtins.input", side_effect=["admin@example.com", "Hazzan", "Admin"]):
            with patch("getpass.getpass", side_effect=[PASSWORD, PASSWORD]):
                with self.assertRaises(CommandError):
                    call_command("create_admin")

    def test_create_admin_command_rejects_password_mismatch(self):
        with patch("builtins.input", side_effect=["admin@example.com", "Hazzan", "Admin"]):
            with patch("getpass.getpass", side_effect=[PASSWORD, "DifferentPass123!"]):
                with self.assertRaises(CommandError):
                    call_command("create_admin")

    def test_create_admin_command_rejects_weak_password(self):
        with patch("builtins.input", side_effect=["admin@example.com", "Hazzan", "Admin"]):
            with patch("getpass.getpass", side_effect=["password", "password"]):
                with self.assertRaises(CommandError):
                    call_command("create_admin")
