export const ROLES = {
  ADMIN: "ADMIN",
  MANAGER: "MANAGER",
  RECEPTIONIST: "RECEPTIONIST",
  ACCOUNTANT: "ACCOUNTANT",
  STAFF: "STAFF",
};

export function hasRole(user, role) {
  return user?.role === role;
}

export function hasAnyRole(user, roles = []) {
  return roles.length === 0 || roles.includes(user?.role);
}

export function can(user, permission) {
  const permissions = {
    "users:view": [ROLES.ADMIN],
    "users:manage": [ROLES.ADMIN],
  };

  return hasAnyRole(user, permissions[permission] ?? []);
}
