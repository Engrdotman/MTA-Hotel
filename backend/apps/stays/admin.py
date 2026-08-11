from django.contrib import admin

from .models import Stay


@admin.register(Stay)
class StayAdmin(admin.ModelAdmin):
    list_display = ("id", "reservation", "guest", "room", "status", "actual_check_in", "actual_check_out")
    list_filter = ("status", "actual_check_in")
    search_fields = ("reservation__reservation_number", "guest__guest_code", "room__room_number")

