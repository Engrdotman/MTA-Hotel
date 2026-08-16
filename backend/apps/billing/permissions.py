from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import has_any_role


class CanAccessBilling(BasePermission):
    """Permission for billing operations."""
    
    # Roles that can create and manage invoices
    manage_roles = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT, Role.RECEPTIONIST)
    
    # Roles that can view billing information
    read_roles = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT, Role.RECEPTIONIST)
    
    # Roles that can record payments
    payment_roles = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        """Check if user can access billing."""
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return has_any_role(request.user, self.read_roles)
        
        # POST (create invoice)
        if request.method == "POST" and "payments" not in request.path:
            return has_any_role(request.user, self.manage_roles)
        
        # POST (record payment) or PATCH (void/issue)
        if request.method in ("POST", "PATCH"):
            return has_any_role(request.user, self.payment_roles)
        
        return False


class CanManageInvoices(BasePermission):
    """Permission to manage (create, issue, void) invoices."""
    
    allowed_roles = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT)

    def has_permission(self, request, view):
        return has_any_role(request.user, self.allowed_roles)


class CanRecordPayments(BasePermission):
    """Permission to record payments."""
    
    allowed_roles = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        return has_any_role(request.user, self.allowed_roles)


