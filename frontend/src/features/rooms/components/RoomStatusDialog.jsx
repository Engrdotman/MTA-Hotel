import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { formatStatus, roomStatuses } from "../roomUtils.js";

export function RoomStatusDialog({ error, isSubmitting, onCancel, onConfirm, room }) {
  const [status, setStatus] = useState("");

  useEffect(() => {
    setStatus(room?.status || "");
  }, [room]);

  if (!room) {
    return null;
  }

  return (
    <div aria-modal="true" className="room-modal" role="dialog">
      <button aria-label="Cancel status change" className="room-modal-backdrop" onClick={onCancel} type="button" />
      <div className="room-status-panel">
        <div className="room-status-icon">
          <RefreshCw aria-hidden="true" size={22} />
        </div>
        <h2>Room {room.room_number}</h2>
        <p>
          Current status: <strong>{formatStatus(room.status)}</strong>
        </p>
        {error ? <p className="room-form-error">{error}</p> : null}
        <label className="room-field">
          <span>Change to</span>
          <select onChange={(event) => setStatus(event.target.value)} value={status}>
            {roomStatuses.map((option) => (
              <option key={option} value={option}>
                {formatStatus(option)}
              </option>
            ))}
          </select>
        </label>
        <div className="room-form-actions">
          <button onClick={onCancel} type="button">
            Cancel
          </button>
          <button disabled={isSubmitting} onClick={() => onConfirm(status)} type="button">
            {isSubmitting ? "Updating..." : "Confirm Change"}
          </button>
        </div>
      </div>
    </div>
  );
}
