from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.guests.models import Guest


class GuestApiTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="RECEPTIONIST")
        self.user = User.objects.create_user(
            email="desk@example.com",
            password="StrongPass123",
            first_name="Desk",
            last_name="Officer",
            role=role,
        )
        self.client.force_authenticate(user=self.user)

    def guest_payload(self, **overrides):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "phone": "08000000000",
            "email": "john@example.com",
            "address": "Maiduguri",
            "id_type": "NATIONAL_ID",
            "id_number": "123456789",
            "nationality": "Nigerian",
            "date_of_birth": "1995-05-10",
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "08000000001",
            "notes": "Regular guest",
        }
        payload.update(overrides)
        return payload

    def create_guest(self, **overrides):
        data = self.guest_payload(**overrides)
        data["guest_code"] = overrides.pop("guest_code", f"GST-{Guest.objects.count() + 1:06d}")
        return Guest.objects.create(**data)

    def test_authenticated_list_returns_paginated_guests(self):
        self.create_guest(first_name="Aisha", email="aisha@example.com")

        response = self.client.get(reverse("guest-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["first_name"], "Aisha")

    def test_unauthenticated_list_is_rejected(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("guest-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_creation_generates_guest_code(self):
        response = self.client.post(reverse("guest-list"), self.guest_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["guest_code"], "GST-000001")
        self.assertTrue(Guest.objects.filter(guest_code="GST-000001").exists())

    def test_guest_code_generation_uses_next_padded_number(self):
        self.create_guest(guest_code="GST-000009")

        response = self.client.post(
            reverse("guest-list"),
            self.guest_payload(email="next@example.com", id_number="NEXT-10"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["guest_code"], "GST-000010")

    def test_invalid_guest_data_is_rejected(self):
        response = self.client.post(
            reverse("guest-list"),
            self.guest_payload(first_name="", phone="bad", date_of_birth="2999-01-01"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)
        self.assertIn("phone", response.data)
        self.assertIn("date_of_birth", response.data)

    def test_guest_retrieval(self):
        guest = self.create_guest(first_name="Musa")

        response = self.client.get(reverse("guest-detail", kwargs={"pk": guest.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Musa")

    def test_guest_update_does_not_change_guest_code(self):
        guest = self.create_guest(guest_code="GST-000100", first_name="Old")

        response = self.client.patch(
            reverse("guest-detail", kwargs={"pk": guest.pk}),
            {"first_name": "New", "guest_code": "GST-999999"},
            format="json",
        )
        guest.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(guest.first_name, "New")
        self.assertEqual(guest.guest_code, "GST-000100")

    def test_guest_delete_without_related_records(self):
        guest = self.create_guest()

        response = self.client.delete(reverse("guest-detail", kwargs={"pk": guest.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Guest.objects.filter(pk=guest.pk).exists())

    def test_guest_search(self):
        self.create_guest(first_name="Hazzan", email="hazzan@example.com")
        self.create_guest(first_name="Other", email="other@example.com", id_number="OTHER")

        response = self.client.get(reverse("guest-list"), {"search": "Hazzan"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["first_name"], "Hazzan")

    def test_guest_filtering(self):
        self.create_guest(nationality="Nigerian", id_type="PASSPORT")
        self.create_guest(nationality="Ghanaian", id_type="NATIONAL_ID", id_number="GH-1")

        response = self.client.get(
            reverse("guest-list"),
            {"nationality": "Nigerian", "id_type": "PASSPORT"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["nationality"], "Nigerian")

    def test_guest_pagination_page_size(self):
        for index in range(25):
            self.create_guest(
                first_name=f"Guest{index}",
                email=f"guest{index}@example.com",
                id_number=f"ID-{index}",
            )

        response = self.client.get(reverse("guest-list"), {"page_size": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 10)
