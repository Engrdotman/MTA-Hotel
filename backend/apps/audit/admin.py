from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "module", "object_type", "object_id", "ip_address")
    list_filter = ("action", "module", "created_at")
    search_fields = ("user__email", "module", "object_type", "object_id", "description")
    readonly_fields = ("created_at",)
