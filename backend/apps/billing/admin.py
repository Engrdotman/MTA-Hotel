from django.contrib import admin

from .models import Invoice, InvoiceItem, StayCharge


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "guest", "reservation", "status", "total", "amount_paid", "balance", "currency", "issued_at")
    list_filter = ("status", "currency", "issued_at")
    search_fields = ("invoice_number", "guest__guest_code", "reservation__reservation_number")
    inlines = [InvoiceItemInline]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "item_type", "description", "quantity", "unit_price", "amount", "service_date")
    list_filter = ("item_type", "service_date")
    search_fields = ("invoice__invoice_number", "description")


@admin.register(StayCharge)
class StayChargeAdmin(admin.ModelAdmin):
    list_display = ("stay", "charge_type", "description", "amount", "service_date", "status", "invoice")
    list_filter = ("charge_type", "status", "service_date")
    search_fields = ("description", "stay__guest__guest_code", "stay__room__room_number", "invoice__invoice_number")
