import { AlertTriangle } from "lucide-react";

import { getGuestName } from "../guestUtils.js";

export function GuestDeleteDialog({ error, guest, isDeleting, onCancel, onConfirm }) {
  if (!guest) {
    return null;
  }

  return (
    <div aria-modal="true" className="guest-modal" role="dialog">
      <button aria-label="Cancel archive" className="guest-modal-backdrop" onClick={onCancel} type="button" />
      <div className="guest-delete-panel">
        <div className="guest-delete-icon">
          <AlertTriangle aria-hidden="true" size={24} />
        </div>
        <h2>Archive guest?</h2>
        <p>Archive {getGuestName(guest)} without deleting bookings, invoices, payments, or receipts.</p>
        {error ? <p className="guest-form-error">{error}</p> : null}
        <div className="guest-form-actions">
          <button onClick={onCancel} type="button">
            Cancel
          </button>
          <button disabled={isDeleting} onClick={onConfirm} type="button">
            {isDeleting ? "Archiving..." : "Archive"}
          </button>
        </div>
      </div>
    </div>
  );
}
