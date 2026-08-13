from rest_framework import serializers

from .models import Room, RoomType


class RoomTypeSerializer(serializers.ModelSerializer):
    room_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RoomType
        fields = [
            "id",
            "name",
            "description",
            "capacity",
            "base_price",
            "room_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "room_count", "created_at", "updated_at"]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Room type name is required.")
        return value.strip()

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0.")
        return value

    def validate_base_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Base price cannot be negative.")
        return value


class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(source="room_type.name", read_only=True)
    room_type_capacity = serializers.IntegerField(source="room_type.capacity", read_only=True)
    room_type_base_price = serializers.DecimalField(
        source="room_type.base_price",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Room
        fields = [
            "id",
            "room_number",
            "room_type",
            "room_type_name",
            "room_type_capacity",
            "room_type_base_price",
            "floor",
            "status",
            "status_display",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "room_type_name",
            "room_type_capacity",
            "room_type_base_price",
            "status_display",
            "created_at",
            "updated_at",
        ]

    def validate_room_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Room number is required.")
        return value.strip()

    def validate_floor(self, value):
        if value and len(value.strip()) > 20:
            raise serializers.ValidationError("Floor is too long.")
        return value.strip() if value else value


class RoomStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Room.Status.choices)
