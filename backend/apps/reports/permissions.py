from rest_framework.permissions import BasePermission

from apps.accounts.models import Role
from apps.accounts.permissions import has_any_role


class CanAccessReports(BasePermission):
    """Permission to access reports."""
    
    allowed_roles = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        return has_any_role(request.user, self.allowed_roles)


class CanAccessFinancialReports(BasePermission):
    """Permission to access financial reports (Revenue, Outstanding)."""
    
    allowed_roles = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT)

    def has_permission(self, request, view):
        return has_any_role(request.user, self.allowed_roles)


class CanAccessOperationalReports(BasePermission):
    """Permission to access operational reports (Occupancy, Reservations)."""
    
    allowed_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        return has_any_role(request.user, self.allowed_roles)
