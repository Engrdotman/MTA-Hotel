from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        PAYMENT = "PAYMENT", "Payment"
        CHECK_IN = "CHECK_IN", "Check in"
        CHECK_OUT = "CHECK_OUT", "Check out"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    module = models.CharField(max_length=50)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"], name="audit_user_idx"),
            models.Index(fields=["module"], name="audit_module_idx"),
            models.Index(fields=["object_type"], name="audit_object_type_idx"),
            models.Index(fields=["object_id"], name="audit_object_id_idx"),
            models.Index(fields=["created_at"], name="audit_created_at_idx"),
        ]

    def __str__(self):
        return f"{self.action} {self.module} {self.object_id}".strip()
