from rest_framework import serializers

from apps.guests.models import Guest
from apps.rooms.models import Room

from .models import Reservation
from .services import create_reservation, has_room_conflict, update_reservation


class ReservationGuestSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Guest
        fields = ["id", "guest_code", "first_name", "last_name", "full_name", "phone", "email"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class ReservationSerializer(serializers.ModelSerializer):
    guest_name = serializers.SerializerMethodField()
    guest_code = serializers.CharField(source="guest.guest_code", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    room_type_name = serializers.CharField(source="room.room_type.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    source_display = serializers.CharField(source="get_source_display", read_only=True)
    nights = serializers.SerializerMethodField()
    additional_guest_ids = serializers.PrimaryKeyRelatedField(
        queryset=Guest.objects.all(),
        many=True,
        required=False,
        source="additional_guests",
        write_only=True,
    )
    additional_guests = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "reservation_number",
            "guest",
            "guest_name",
            "guest_code",
            "room",
            "room_number",
            "room_type_name",
            "check_in_date",
            "check_out_date",
            "nights",
            "adults",
            "children",
            "status",
            "status_display",
            "source",
            "source_display",
            "special_requests",
            "notes",
            "additional_guest_ids",
            "additional_guests",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reservation_number",
            "guest_name",
            "guest_code",
            "room_number",
            "room_type_name",
            "status_display",
            "source_display",
            "nights",
            "additional_guests",
            "created_at",
            "updated_at",
        ]

    def get_guest_name(self, obj):
        return f"{obj.guest.first_name} {obj.guest.last_name}".strip()

    def get_nights(self, obj):
        return (obj.check_out_date - obj.check_in_date).days

    def get_additional_guests(self, obj):
        guests = [link.guest for link in obj.reservation_guests.all() if not link.is_primary]
        return ReservationGuestSummarySerializer(guests, many=True).data

    def validate(self, attrs):
        attrs = super().validate(attrs)

        guest = attrs.get("guest", getattr(self.instance, "guest", None))
        room = attrs.get("room", getattr(self.instance, "room", None))
        check_in_date = attrs.get("check_in_date", getattr(self.instance, "check_in_date", None))
        check_out_date = attrs.get("check_out_date", getattr(self.instance, "check_out_date", None))
        adults = attrs.get("adults", getattr(self.instance, "adults", 1))
        children = attrs.get("children", getattr(self.instance, "children", 0))
        additional_guests = attrs.get("additional_guests", None)

        if check_in_date and check_out_date and check_out_date <= check_in_date:
            raise serializers.ValidationError({"check_out_date": "Check-out date must be after check-in date."})

        if adults <= 0:
            raise serializers.ValidationError({"adults": "At least one adult is required."})

        if children < 0:
            raise serializers.ValidationError({"children": "Children cannot be negative."})

        if room and check_in_date and check_out_date:
            exclude_id = self.instance.pk if self.instance else None
            if has_room_conflict(room, check_in_date, check_out_date, exclude_reservation_id=exclude_id):
                raise serializers.ValidationError({"room": "This room already has an active reservation for these dates."})

        if guest and additional_guests and guest in additional_guests:
            raise serializers.ValidationError({"additional_guest_ids": "The primary guest is already included."})

        return attrs

    def create(self, validated_data):
        additional_guests = validated_data.pop("additional_guests", [])
        return create_reservation(
            {**validated_data, "additional_guest_ids": [guest.id for guest in additional_guests]},
            created_by=self.context["request"].user,
        )

    def update(self, instance, validated_data):
        additional_guests = validated_data.pop("additional_guests", None)
        if additional_guests is not None:
            validated_data["additional_guest_ids"] = [guest.id for guest in additional_guests]
        return update_reservation(instance, validated_data)


class ReservationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Reservation.Status.choices)
