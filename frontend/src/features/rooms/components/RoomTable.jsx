import { Edit3, Eye, RefreshCw, Trash2 } from "lucide-react";

import { formatCurrency, formatStatus } from "../roomUtils.js";

export function RoomTable({ isFiltered, onDelete, onEdit, onStatus, onView, rooms }) {
  if (!rooms.length) {
    return <div className="room-empty">{isFiltered ? "No rooms match your filters." : "No rooms found."}</div>;
  }

  return (
    <div className="room-table-wrap">
      <table className="room-table">
        <thead>
          <tr>
            <th>Room</th>
            <th>Room Type</th>
            <th>Floor</th>
            <th>Price</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rooms.map((room) => (
            <tr key={room.id}>
              <td data-label="Room">
                <strong>Room {room.room_number}</strong>
              </td>
              <td data-label="Room Type">{room.room_type_name}</td>
              <td data-label="Floor">{room.floor || "-"}</td>
              <td data-label="Price">{formatCurrency(room.room_type_base_price)}</td>
              <td data-label="Status">
                <span className={`room-status-badge room-status-${room.status.toLowerCase()}`}>
                  {formatStatus(room.status)}
                </span>
              </td>
              <td data-label="Actions">
                <div className="room-actions">
                  <button aria-label={`View room ${room.room_number}`} onClick={() => onView(room)} type="button">
                    <Eye aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Edit room ${room.room_number}`} onClick={() => onEdit(room)} type="button">
                    <Edit3 aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Change room ${room.room_number} status`} onClick={() => onStatus(room)} type="button">
                    <RefreshCw aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Delete room ${room.room_number}`} onClick={() => onDelete(room)} type="button">
                    <Trash2 aria-hidden="true" size={16} />
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
