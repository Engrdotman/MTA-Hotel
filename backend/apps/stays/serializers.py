from rest_framework import serializers

from .models import Stay


class StayReservationSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    reservation_number = serializers.CharField()
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField()
    adults = serializers.IntegerField()
    children = serializers.IntegerField()


class StayGuestSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    guest_code = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.SerializerMethodField()
    phone = serializers.CharField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class StayRoomSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    room_number = serializers.CharField()
    room_type_name = serializers.CharField(source="room_type.name")
    status = serializers.CharField()


class StayUserSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class StaySerializer(serializers.ModelSerializer):
    reservation = StayReservationSummarySerializer(read_only=True)
    guest = StayGuestSummarySerializer(read_only=True)
    room = StayRoomSummarySerializer(read_only=True)
    checked_in_by = StayUserSummarySerializer(read_only=True)
    checked_out_by = StayUserSummarySerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Stay
        fields = [
            "id",
            "reservation",
            "guest",
            "room",
            "checked_in_at",
            "checked_out_at",
            "checked_in_by",
            "checked_out_by",
            "status",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CheckInSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)


class CheckOutSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
