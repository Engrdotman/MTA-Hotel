from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from apps.audit.models import AuditLog


INVALID_CREDENTIALS_MESSAGE = "Invalid email or password."


def authenticate_user(email, password, request=None):
    user = authenticate(request=request, username=email, password=password)

    if user is None or not user.is_active:
        raise AuthenticationFailed(INVALID_CREDENTIALS_MESSAGE)

    return user


def build_user_response(user, include_account_status=True):
    role = user.role.name if user.role else None

    data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role,
    }

    if include_account_status:
        data["phone"] = user.phone
        data["is_active"] = user.is_active

    return data


def build_login_response(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": build_user_response(user, include_account_status=False),
    }


def blacklist_refresh_token(refresh_token):
    token = RefreshToken(refresh_token)
    token.blacklist()


def record_auth_event(user, action, request=None):
    ip_address = _get_client_ip(request)
    AuditLog.objects.create(
        user=user,
        action=action,
        module="accounts",
        object_type="User",
        object_id=str(user.id),
        description=f"User {action.lower()} event.",
        ip_address=ip_address,
    )


def _get_client_ip(request):
    if request is None:
        return None

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")
