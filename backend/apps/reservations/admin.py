from django.contrib import admin

from .models import Reservation, ReservationGuest


class ReservationGuestInline(admin.TabularInline):
    model = ReservationGuest
    extra = 0


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("reservation_number", "guest", "room", "check_in_date", "check_out_date", "status", "source")
    list_filter = ("status", "source", "check_in_date", "check_out_date")
    search_fields = ("reservation_number", "guest__guest_code", "guest__first_name", "guest__last_name", "room__room_number")
    inlines = [ReservationGuestInline]


@admin.register(ReservationGuest)
class ReservationGuestAdmin(admin.ModelAdmin):
    list_display = ("reservation", "guest", "is_primary", "created_at")
    list_filter = ("is_primary",)
    search_fields = ("reservation__reservation_number", "guest__guest_code", "guest__first_name", "guest__last_name")

