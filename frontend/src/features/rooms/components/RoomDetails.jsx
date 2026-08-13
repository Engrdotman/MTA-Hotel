import { X } from "lucide-react";

import { formatCurrency, formatDate, formatStatus } from "../roomUtils.js";

export function RoomDetails({ onClose, room }) {
  if (!room) {
    return null;
  }

  const rows = [
    ["Room Number", room.room_number],
    ["Room Type", room.room_type_name],
    ["Capacity", room.room_type_capacity],
    ["Base Price", formatCurrency(room.room_type_base_price)],
    ["Floor", room.floor],
    ["Status", formatStatus(room.status)],
    ["Description", room.description],
    ["Created", formatDate(room.created_at)],
    ["Updated", formatDate(room.updated_at)],
  ];

  return (
    <aside aria-modal="true" className="room-drawer" role="dialog">
      <button aria-label="Close room details" className="room-modal-backdrop" onClick={onClose} type="button" />
      <div className="room-drawer-panel">
        <div className="room-modal-heading">
          <div>
            <h2>Room {room.room_number}</h2>
            <p>{room.room_type_name}</p>
          </div>
          <button aria-label="Close room details" onClick={onClose} type="button">
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        <dl className="room-details-list">
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
