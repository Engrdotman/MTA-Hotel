from django.urls import path

from .views import LoginView, LogoutView, MeView, RefreshTokenView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("token/refresh/", RefreshTokenView.as_view(), name="auth-token-refresh"),
]
