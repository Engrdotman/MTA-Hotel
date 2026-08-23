from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.rooms.models import Room, RoomType


class RoomsApiTests(APITestCase):
    def setUp(self):
        role = Role.objects.create(name="MANAGER")
        self.user = User.objects.create_user(
            email="manager@example.com",
            password="StrongPass123",
            first_name="Room",
            last_name="Manager",
            role=role,
        )
        self.client.force_authenticate(user=self.user)

    def room_type_payload(self, **overrides):
        payload = {
            "name": "Standard",
            "description": "Comfortable standard room.",
            "capacity": 2,
            "max_adults": 2,
            "max_children": 2,
            "base_price": "25000.00",
        }
        payload.update(overrides)
        return payload

    def create_room_type(self, **overrides):
        payload = self.room_type_payload(**overrides)
        return RoomType.objects.create(**payload)

    def room_payload(self, room_type=None, **overrides):
        room_type = room_type or self.create_room_type()
        payload = {
            "room_number": "101",
            "room_type": room_type.id,
            "floor": "1",
            "status": Room.Status.AVAILABLE,
            "description": "Near reception.",
        }
        payload.update(overrides)
        return payload

    def create_room(self, room_type=None, **overrides):
        room_type = room_type or self.create_room_type()
        payload = self.room_payload(room_type=room_type, **overrides)
        payload["room_type"] = room_type
        return Room.objects.create(**payload)

    def test_create_room_type(self):
        response = self.client.post(reverse("room-type-list"), self.room_type_payload(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Standard")
        self.assertEqual(RoomType.objects.count(), 1)

    def test_duplicate_room_type_is_rejected(self):
        self.create_room_type(name="Deluxe")

        response = self.client.post(
            reverse("room-type-list"),
            self.room_type_payload(name="Deluxe"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_invalid_capacity_is_rejected(self):
        response = self.client.post(
            reverse("room-type-list"),
            self.room_type_payload(capacity=0),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("capacity", response.data)

    def test_room_type_adult_and_child_limits_are_validated(self):
        response = self.client.post(
            reverse("room-type-list"),
            self.room_type_payload(capacity=2, max_adults=3, max_children=1),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("max_adults", response.data)

        response = self.client.post(
            reverse("room-type-list"),
            self.room_type_payload(name="Child Limit", capacity=2, max_adults=2, max_children=3),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("max_children", response.data)

    def test_negative_price_is_rejected(self):
        response = self.client.post(
            reverse("room-type-list"),
            self.room_type_payload(base_price="-1.00"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("base_price", response.data)

    def test_create_room(self):
        room_type = self.create_room_type()

        response = self.client.post(
            reverse("room-list"),
            self.room_payload(room_type=room_type),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["room_number"], "101")
        self.assertEqual(response.data["room_type_name"], "Standard")

    def test_duplicate_room_number_is_rejected(self):
        room_type = self.create_room_type()
        self.create_room(room_type=room_type, room_number="201")

        response = self.client.post(
            reverse("room-list"),
            self.room_payload(room_type=room_type, room_number="201"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("room_number", response.data)

    def test_invalid_status_is_rejected(self):
        room_type = self.create_room_type()

        response = self.client.post(
            reverse("room-list"),
            self.room_payload(room_type=room_type, status="BROKEN"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("status", response.data)

    def test_update_room(self):
        room_type = self.create_room_type()
        deluxe = self.create_room_type(name="Deluxe", base_price=Decimal("40000.00"))
        room = self.create_room(room_type=room_type, floor="1")

        response = self.client.patch(
            reverse("room-detail", kwargs={"pk": room.pk}),
            {"room_type": deluxe.id, "floor": "2", "description": "Updated"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["room_type_name"], "Deluxe")
        self.assertEqual(response.data["floor"], "2")

    def test_change_room_status(self):
        room = self.create_room()

        response = self.client.patch(
            reverse("room-status", kwargs={"pk": room.pk}),
            {"status": Room.Status.MAINTENANCE},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Room.Status.MAINTENANCE)

    def test_room_filtering(self):
        room_type = self.create_room_type(name="Standard")
        deluxe = self.create_room_type(name="Deluxe")
        self.create_room(room_type=room_type, room_number="101", floor="1", status=Room.Status.AVAILABLE)
        self.create_room(room_type=deluxe, room_number="202", floor="2", status=Room.Status.OCCUPIED)

        response = self.client.get(
            reverse("room-list"),
            {"status": Room.Status.OCCUPIED, "room_type": deluxe.id, "floor": "2"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["room_number"], "202")

    def test_room_searching(self):
        room_type = self.create_room_type()
        self.create_room(room_type=room_type, room_number="101")
        self.create_room(room_type=room_type, room_number="302")

        response = self.client.get(reverse("room-list"), {"search": "101"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["room_number"], "101")

    def test_pagination(self):
        room_type = self.create_room_type()
        for index in range(25):
            self.create_room(room_type=room_type, room_number=f"{index + 100}")

        response = self.client.get(reverse("room-list"), {"page_size": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 10)

    def test_prevent_deleting_room_type_with_associated_rooms(self):
        room_type = self.create_room_type()
        self.create_room(room_type=room_type)

        response = self.client.delete(reverse("room-type-detail", kwargs={"pk": room_type.pk}))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("rooms are currently assigned", response.data["detail"])

    def test_authentication_required(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("room-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
