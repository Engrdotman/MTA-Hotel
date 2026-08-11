from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Role, User


class AccountsModelTests(TestCase):
    def test_role_name_is_unique(self):
        Role.objects.create(name="MANAGER")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Role.objects.create(name="MANAGER")

    def test_user_uses_email_as_login_identifier(self):
        role = Role.objects.create(name="STAFF")
        user = User.objects.create_user(
            email="frontdesk@example.com",
            password="secret",
            first_name="Front",
            last_name="Desk",
            role=role,
        )

        self.assertEqual(user.email, "frontdesk@example.com")
        self.assertTrue(user.check_password("secret"))


class AuthenticationEndpointTests(APITestCase):
    def setUp(self):
        self.role = Role.objects.create(name="ADMIN")
        self.user = User.objects.create_user(
            email="admin@example.com",
            password="StrongPass123",
            first_name="Hazzan",
            last_name="Admin",
            phone="+2348000000000",
            role=self.role,
        )

    def test_valid_login_returns_tokens_and_user(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@example.com", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "admin@example.com")
        self.assertEqual(response.data["user"]["role"], "ADMIN")
        self.assertNotIn("password", response.data["user"])

    def test_invalid_password_is_rejected_without_user_leak(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@example.com", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid email or password.")

    def test_nonexistent_user_is_rejected_like_invalid_password(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "missing@example.com", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid email or password.")

    def test_inactive_user_is_rejected(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@example.com", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Invalid email or password.")

    def test_authenticated_me_returns_current_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "admin@example.com")
        self.assertEqual(response.data["phone"], "+2348000000000")
        self.assertEqual(response.data["role"], "ADMIN")
        self.assertTrue(response.data["is_active"])
        self.assertNotIn("password", response.data)

    def test_unauthenticated_me_is_rejected(self):
        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_returns_access_token(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            reverse("auth-token-refresh"),
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.force_authenticate(user=self.user)

        logout_response = self.client.post(
            reverse("auth-logout"),
            {"refresh": str(refresh)},
            format="json",
        )
        refresh_response = self.client.post(
            reverse("auth-token-refresh"),
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
