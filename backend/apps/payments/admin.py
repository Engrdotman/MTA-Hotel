from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_reference", "invoice", "amount", "method", "status", "paid_at", "received_by")
    list_filter = ("method", "status", "paid_at")
    search_fields = ("payment_reference", "transaction_reference", "invoice__invoice_number")

