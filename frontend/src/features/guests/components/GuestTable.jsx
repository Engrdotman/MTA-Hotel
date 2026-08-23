import { Archive, Edit3, Eye } from "lucide-react";

import { formatDate, getGuestInitials, getGuestName } from "../guestUtils.js";

export function GuestTable({ guests, isFiltered, onDelete, onEdit, onView }) {
  if (!guests.length) {
    return (
      <div className="guest-empty">
        {isFiltered ? "No guests match your search." : "No guests found."}
      </div>
    );
  }

  return (
    <div className="guest-table-wrap">
      <table className="guest-table">
        <thead>
          <tr>
            <th>Guest Code</th>
            <th>Guest</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Nationality</th>
            <th>ID</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {guests.map((guest) => (
            <tr key={guest.id}>
              <td data-label="Guest Code">{guest.guest_code}</td>
              <td data-label="Guest">
                <div className="guest-person">
                  <span>{getGuestInitials(guest)}</span>
                  <strong>{getGuestName(guest)}</strong>
                </div>
              </td>
              <td data-label="Phone">{guest.phone || "-"}</td>
              <td data-label="Email">{guest.email || "-"}</td>
              <td data-label="Nationality">{guest.nationality || "-"}</td>
              <td data-label="ID">
                {guest.id_type || guest.id_number ? (
                  <span>{[guest.id_type, guest.id_number].filter(Boolean).join(" / ")}</span>
                ) : (
                  "-"
                )}
              </td>
              <td data-label="Created">{formatDate(guest.created_at)}</td>
              <td data-label="Actions">
                <div className="guest-actions">
                  <button aria-label={`View ${getGuestName(guest)}`} onClick={() => onView(guest)} type="button">
                    <Eye aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Edit ${getGuestName(guest)}`} onClick={() => onEdit(guest)} type="button">
                    <Edit3 aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Archive ${getGuestName(guest)}`} onClick={() => onDelete(guest)} type="button">
                    <Archive aria-hidden="true" size={16} />
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
