import { X } from "lucide-react";

import { formatDate } from "../../rooms/roomUtils.js";
import { UserRoleBadge } from "./UserRoleBadge.jsx";

export function UserDetails({ onClose, user }) {
  if (!user) {
    return null;
  }

  return (
    <div className="room-modal-backdrop" role="presentation">
      <section aria-label="User details" className="room-modal user-details-modal">
        <button aria-label="Close user details" className="room-modal-close" onClick={onClose} type="button">
          <X aria-hidden="true" size={18} />
        </button>
        <div>
          <p className="dashboard-kicker">User Details</p>
          <h3>{user.first_name} {user.last_name}</h3>
        </div>
        <dl className="room-details-grid">
          <div><dt>Email</dt><dd>{user.email}</dd></div>
          <div><dt>Phone</dt><dd>{user.phone || "-"}</dd></div>
          <div><dt>Role</dt><dd><UserRoleBadge role={user.role} /></dd></div>
          <div><dt>Status</dt><dd>{user.is_active ? "Active" : "Inactive"}</dd></div>
          <div><dt>Created</dt><dd>{formatDate(user.created_at)}</dd></div>
        </dl>
      </section>
    </div>
  );
}
