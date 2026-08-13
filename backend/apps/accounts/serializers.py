from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import Role, User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=False)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(trim_whitespace=False)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(allow_blank=True)
    role = serializers.CharField(allow_null=True)
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class StaffUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="role.name", read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "role", "is_active", "created_at")
        read_only_fields = ("id", "email", "first_name", "last_name", "phone", "role", "created_at")


class StaffUserCreateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.STAFF_CREATION_ROLES)
    temporary_password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "temporary_password",
            "confirm_password",
            "is_active",
        )

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, attrs):
        password = attrs.get("temporary_password")
        if password != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        validate_password(password)
        return attrs

    def create(self, validated_data):
        role_name = validated_data.pop("role")
        password = validated_data.pop("temporary_password")
        validated_data.pop("confirm_password")
        role, _ = Role.objects.get_or_create(name=role_name)
        return User.objects.create_user(
            password=password,
            role=role,
            is_staff=False,
            is_superuser=False,
            **validated_data,
        )


class StaffUserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.STAFF_CREATION_ROLES, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "role", "is_active")

    def update(self, instance, validated_data):
        role_name = validated_data.pop("role", None)
        if role_name is not None:
            instance.role, _ = Role.objects.get_or_create(name=role_name)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.is_staff = False
        instance.is_superuser = False
        instance.save()
        return instance
