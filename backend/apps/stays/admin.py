from django.contrib import admin

from .models import Stay


@admin.register(Stay)
class StayAdmin(admin.ModelAdmin):
    list_display = ("id", "reservation", "guest", "room", "status", "checked_in_at", "checked_out_at")
    list_filter = ("status", "checked_in_at")
    search_fields = ("reservation__reservation_number", "guest__guest_code", "room__room_number")
