from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView

from apps.audit.models import AuditLog

from .models import User
from .permissions import IsAdmin
from .serializers import LoginSerializer, LogoutSerializer
from .serializers import StaffUserCreateSerializer, StaffUserSerializer, StaffUserUpdateSerializer
from .services import (
    authenticate_user,
    blacklist_refresh_token,
    build_login_response,
    build_user_response,
    record_auth_event,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate_user(
            serializer.validated_data["email"],
            serializer.validated_data["password"],
            request=request,
        )
        record_auth_event(user, AuditLog.Action.LOGIN, request)

        return Response(build_login_response(user), status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            blacklist_refresh_token(serializer.validated_data["refresh"])
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record_auth_event(request.user, AuditLog.Action.LOGOUT, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(build_user_response(request.user), status=status.HTTP_200_OK)


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related("role").order_by("email")
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_serializer_class(self):
        if self.action == "create":
            return StaffUserCreateSerializer
        if self.action in ("partial_update", "update"):
            return StaffUserUpdateSerializer
        return StaffUserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
