from rest_framework.permissions import BasePermission

from apps.accounts.models import Role


def get_user_role(user):
    if not user or not user.is_authenticated or not user.is_active or not user.role:
        return None
    return user.role.name


def has_role(user, role):
    return get_user_role(user) == role


def has_any_role(user, roles):
    return get_user_role(user) in roles


class RolePermission(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        return has_any_role(request.user, self.allowed_roles)


class IsAdmin(RolePermission):
    allowed_roles = (Role.ADMIN,)


class IsManager(RolePermission):
    allowed_roles = (Role.MANAGER,)


class IsReceptionist(RolePermission):
    allowed_roles = (Role.RECEPTIONIST,)


class IsAccountant(RolePermission):
    allowed_roles = (Role.ACCOUNTANT,)


class IsStaff(RolePermission):
    allowed_roles = (Role.STAFF,)


class IsHotelOperator(RolePermission):
    allowed_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST)


class CanAccessGuests(BasePermission):
    read_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST, Role.ACCOUNTANT, Role.STAFF)
    write_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return has_any_role(request.user, self.read_roles)
        return has_any_role(request.user, self.write_roles)


class CanAccessRooms(BasePermission):
    read_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST, Role.STAFF)
    write_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return has_any_role(request.user, self.read_roles)
        return has_any_role(request.user, self.write_roles)


class CanAccessReservations(BasePermission):
    read_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST, Role.ACCOUNTANT)
    write_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return has_any_role(request.user, self.read_roles)
        return has_any_role(request.user, self.write_roles)


class CanAccessStays(BasePermission):
    read_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST, Role.ACCOUNTANT)
    write_roles = (Role.ADMIN, Role.MANAGER, Role.RECEPTIONIST)

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return has_any_role(request.user, self.read_roles)
        return has_any_role(request.user, self.write_roles)


class CanManageUsers(BasePermission):
    """Permission for user management endpoints"""
    
    def has_permission(self, request, view):
        # Manager and Admin can manage users, but managers can only see/create staff users
        return has_any_role(request.user, (Role.ADMIN, Role.MANAGER))
    
    def has_object_permission(self, request, view, obj):
        user_role = get_user_role(request.user)
        # Admin can do anything
        if user_role == Role.ADMIN:
            return True
        # Manager cannot modify other managers or admins
        if user_role == Role.MANAGER:
            obj_role = get_user_role(obj)
            return obj_role not in (Role.ADMIN, Role.MANAGER)
        return False
