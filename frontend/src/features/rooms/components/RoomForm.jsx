import { X } from "lucide-react";
import { useEffect, useState } from "react";

import { formatStatus, mapValidationErrors, roomStatuses } from "../roomUtils.js";

const emptyValues = {
  room_number: "",
  room_type: "",
  floor: "",
  status: "AVAILABLE",
  description: "",
};

export function RoomForm({ error, isSubmitting, onClose, onSubmit, room, roomTypes }) {
  const [values, setValues] = useState(emptyValues);
  const [fieldErrors, setFieldErrors] = useState({});

  useEffect(() => {
    setValues(room ? { ...emptyValues, ...room, room_type: String(room.room_type) } : emptyValues);
    setFieldErrors({});
  }, [room]);

  useEffect(() => {
    setFieldErrors(mapValidationErrors(error));
  }, [error]);

  function updateField(event) {
    const { name, value } = event.target;
    setValues((current) => ({ ...current, [name]: value }));
    setFieldErrors((current) => ({ ...current, [name]: undefined }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(values);
  }

  return (
    <div aria-modal="true" className="room-modal" role="dialog">
      <button aria-label="Close room form" className="room-modal-backdrop" onClick={onClose} type="button" />
      <form className="room-panel" onSubmit={handleSubmit}>
        <div className="room-modal-heading">
          <div>
            <h2>{room ? "Edit Room" : "Add Room"}</h2>
            <p>{room ? "Update room details." : "Create a new room."}</p>
          </div>
          <button aria-label="Close room form" onClick={onClose} type="button">
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        {error && !Object.keys(fieldErrors).length ? <p className="room-form-error">{error}</p> : null}

        <div className="room-form-grid">
          <RoomField
            disabled={Boolean(room)}
            error={fieldErrors.room_number}
            label="Room Number *"
            name="room_number"
            onChange={updateField}
            value={values.room_number}
          />
          <label className="room-field">
            <span>Room Type *</span>
            <select aria-invalid={Boolean(fieldErrors.room_type)} name="room_type" onChange={updateField} value={values.room_type}>
              <option value="">Select room type</option>
              {roomTypes.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
            {fieldErrors.room_type ? <small>{fieldErrors.room_type[0]}</small> : null}
          </label>
          <RoomField error={fieldErrors.floor} label="Floor" name="floor" onChange={updateField} value={values.floor} />
          {!room ? (
            <label className="room-field">
              <span>Status</span>
              <select name="status" onChange={updateField} value={values.status}>
                {roomStatuses.map((status) => (
                  <option key={status} value={status}>
                    {formatStatus(status)}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label className="room-field room-field-wide">
            <span>Description</span>
            <textarea name="description" onChange={updateField} rows={4} value={values.description || ""} />
          </label>
        </div>

        <div className="room-form-actions">
          <button onClick={onClose} type="button">
            Cancel
          </button>
          <button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Saving..." : "Save Room"}
          </button>
        </div>
      </form>
    </div>
  );
}

function RoomField({ disabled = false, error, label, name, onChange, value }) {
  return (
    <label className="room-field">
      <span>{label}</span>
      <input aria-invalid={Boolean(error)} disabled={disabled} name={name} onChange={onChange} value={value || ""} />
      {error ? <small>{Array.isArray(error) ? error[0] : error}</small> : null}
    </label>
  );
}
