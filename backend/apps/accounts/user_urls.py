from django.urls import path

from .views import UserViewSet

user_list = UserViewSet.as_view({"get": "list", "post": "create"})
user_detail = UserViewSet.as_view(
    {"get": "retrieve", "patch": "partial_update", "put": "update", "delete": "destroy"}
)

urlpatterns = [
    path("", user_list, name="user-list"),
    path("<int:pk>/", user_detail, name="user-detail"),
]
