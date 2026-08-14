from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_reference", "invoice", "amount", "method", "payment_date", "received_by", "created_at")
    list_filter = ("method", "payment_date", "created_at")
    search_fields = ("payment_reference", "invoice__invoice_number")
    readonly_fields = ("created_at", "updated_at")
