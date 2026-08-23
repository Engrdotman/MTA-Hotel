import { X } from "lucide-react";

import { formatDate, getGuestName } from "../guestUtils.js";

export function GuestDetails({ guest, onClose }) {
  if (!guest) {
    return null;
  }

  const rows = [
    ["Guest Code", guest.guest_code],
    ["Full Name", getGuestName(guest)],
    ["Phone", guest.phone],
    ["Email", guest.email],
    ["Address", guest.address],
    ["ID Information", [guest.id_type, guest.id_number].filter(Boolean).join(" / ")],
    ["Nationality", guest.nationality],
    ["Date of Birth", formatDate(guest.date_of_birth)],
    ["Emergency Contact", [guest.emergency_contact_name, guest.emergency_contact_phone].filter(Boolean).join(" / ")],
    ["Status", guest.is_active ? "Active" : "Archived"],
    ["Notes", guest.notes],
    ["Created Date", formatDate(guest.created_at)],
    ["Updated Date", formatDate(guest.updated_at)],
  ];

  return (
    <aside aria-modal="true" className="guest-details-drawer" role="dialog">
      <button aria-label="Close details" className="guest-modal-backdrop" onClick={onClose} type="button" />
      <div className="guest-details-panel">
        <div className="guest-modal-heading">
          <div>
            <h2>{getGuestName(guest)}</h2>
            <p>{guest.guest_code}</p>
          </div>
          <button aria-label="Close details" onClick={onClose} type="button">
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        <dl className="guest-details-list">
          {rows.map(([label, value]) => (
            <div key={label}>
              <dt>{label}</dt>
              <dd>{value || "-"}</dd>
            </div>
          ))}
        </dl>
      </div>
    </aside>
  );
}
