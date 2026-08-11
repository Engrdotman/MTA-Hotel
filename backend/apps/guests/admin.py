from django.contrib import admin

from .models import Guest


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("guest_code", "first_name", "last_name", "phone", "email", "nationality")
    search_fields = ("guest_code", "first_name", "last_name", "phone", "email", "id_number")
    list_filter = ("nationality", "id_type")

