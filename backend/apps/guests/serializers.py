import re

from django.utils import timezone
from rest_framework import serializers

from .models import Guest
from .services import create_guest


PHONE_PATTERN = re.compile(r"^\+?[0-9\s().-]{7,30}$")


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = [
            "id",
            "guest_code",
            "first_name",
            "last_name",
            "phone",
            "email",
            "address",
            "id_type",
            "id_number",
            "nationality",
            "date_of_birth",
            "emergency_contact_name",
            "emergency_contact_phone",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "guest_code", "created_at", "updated_at"]

    def validate_first_name(self, value):
        return self._validate_required_name(value, "First name")

    def validate_last_name(self, value):
        return self._validate_required_name(value, "Last name")

    def validate_phone(self, value):
        return self._validate_phone(value, "Phone")

    def validate_emergency_contact_phone(self, value):
        return self._validate_phone(value, "Emergency contact phone")

    def validate_date_of_birth(self, value):
        if value and value > timezone.localdate():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def create(self, validated_data):
        return create_guest(validated_data)

    def _validate_required_name(self, value, label):
        if not value or not value.strip():
            raise serializers.ValidationError(f"{label} is required.")
        return value.strip()

    def _validate_phone(self, value, label):
        if value and not PHONE_PATTERN.match(value):
            raise serializers.ValidationError(f"{label} format is invalid.")
        return value
