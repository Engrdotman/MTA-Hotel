import { Edit3, Eye, UserX } from "lucide-react";

import { formatDate } from "../../rooms/roomUtils.js";
import { UserRoleBadge } from "./UserRoleBadge.jsx";

export function UserTable({ onDeactivate, onEdit, onView, users }) {
  if (!users.length) {
    return <div className="room-empty">No users found.</div>;
  }

  return (
    <div className="room-table-wrap">
      <table className="room-table user-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Role</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td data-label="Name">
                <strong>{user.first_name} {user.last_name}</strong>
              </td>
              <td data-label="Email">{user.email}</td>
              <td data-label="Phone">{user.phone || "-"}</td>
              <td data-label="Role"><UserRoleBadge role={user.role} /></td>
              <td data-label="Status">
                <span className={`user-status ${user.is_active ? "user-status-active" : "user-status-inactive"}`}>
                  {user.is_active ? "Active" : "Inactive"}
                </span>
              </td>
              <td data-label="Created">{formatDate(user.created_at)}</td>
              <td data-label="Actions">
                <div className="room-actions">
                  <button aria-label={`View ${user.email}`} onClick={() => onView(user)} type="button">
                    <Eye aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Edit ${user.email}`} onClick={() => onEdit(user)} type="button">
                    <Edit3 aria-hidden="true" size={16} />
                  </button>
                  <button disabled={!user.is_active} aria-label={`Deactivate ${user.email}`} onClick={() => onDeactivate(user)} type="button">
                    <UserX aria-hidden="true" size={16} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
