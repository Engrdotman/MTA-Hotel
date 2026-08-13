export function UserRoleBadge({ role }) {
  return <span className={`user-role-badge user-role-${role?.toLowerCase()}`}>{formatRole(role)}</span>;
}

export function formatRole(role) {
  return role
    ? role
        .toLowerCase()
        .split("_")
        .map((part) => part[0].toUpperCase() + part.slice(1))
        .join(" ")
    : "-";
}
