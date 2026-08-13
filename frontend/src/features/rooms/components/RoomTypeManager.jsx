import { Edit3, Plus, Trash2, X } from "lucide-react";
import { useEffect, useState } from "react";

import { formatCurrency, getApiErrorMessage, mapValidationErrors } from "../roomUtils.js";
import {
  createRoomType,
  deleteRoomType,
  getRoomTypes,
  updateRoomType,
} from "../services/roomService.js";

const emptyType = { name: "", description: "", capacity: 1, base_price: "0.00" };

export function RoomTypeManager({ isOpen, onClose, onChanged }) {
  const [roomTypes, setRoomTypes] = useState([]);
  const [editingType, setEditingType] = useState(null);
  const [values, setValues] = useState(emptyType);
  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadTypes();
      setEditingType(null);
      setValues(emptyType);
    }
  }, [isOpen]);

  async function loadTypes() {
    setIsLoading(true);
    setError("");
    try {
      const response = await getRoomTypes({ page_size: 100, ordering: "name" });
      setRoomTypes(response.results || []);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }

  function startEdit(type) {
    setEditingType(type);
    setValues({
      name: type.name,
      description: type.description || "",
      capacity: type.capacity,
      base_price: type.base_price,
    });
    setFieldErrors({});
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);
    setFieldErrors({});
    setError("");
    try {
      if (editingType) {
        await updateRoomType(editingType.id, values);
      } else {
        await createRoomType(values);
      }
      setEditingType(null);
      setValues(emptyType);
      await loadTypes();
      onChanged();
    } catch (requestError) {
      setFieldErrors(mapValidationErrors(requestError));
      setError(getApiErrorMessage(requestError));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(type) {
    setError("");
    try {
      await deleteRoomType(type.id);
      await loadTypes();
      onChanged();
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    }
  }

  if (!isOpen) {
    return null;
  }

  return (
    <div aria-modal="true" className="room-modal" role="dialog">
      <button aria-label="Close room type manager" className="room-modal-backdrop" onClick={onClose} type="button" />
      <div className="room-type-panel">
        <div className="room-modal-heading">
          <div>
            <h2>Manage Room Types</h2>
            <p>Add and maintain room type pricing and capacity.</p>
          </div>
          <button aria-label="Close room type manager" onClick={onClose} type="button">
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        {error ? <p className="room-form-error">{error}</p> : null}

        <form className="room-type-form" onSubmit={handleSubmit}>
          <RoomTypeField error={fieldErrors.name} label="Name *" name="name" onChange={setValues} values={values} />
          <RoomTypeField error={fieldErrors.capacity} label="Capacity *" name="capacity" onChange={setValues} type="number" values={values} />
          <RoomTypeField error={fieldErrors.base_price} label="Base Price *" name="base_price" onChange={setValues} type="number" values={values} />
          <RoomTypeField label="Description" name="description" onChange={setValues} values={values} />
          <button disabled={isSubmitting} type="submit">
            <Plus aria-hidden="true" size={16} />
            {editingType ? "Update Type" : "Add Type"}
          </button>
        </form>

        <div className="room-type-list">
          {isLoading ? (
            <p>Loading room types...</p>
          ) : (
            roomTypes.map((type) => (
              <article key={type.id}>
                <div>
                  <strong>{type.name}</strong>
                  <span>
                    Capacity {type.capacity} / {formatCurrency(type.base_price)} / {type.room_count || 0} rooms
                  </span>
                </div>
                <div>
                  <button aria-label={`Edit ${type.name}`} onClick={() => startEdit(type)} type="button">
                    <Edit3 aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Delete ${type.name}`} onClick={() => handleDelete(type)} type="button">
                    <Trash2 aria-hidden="true" size={16} />
                  </button>
                </div>
              </article>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function RoomTypeField({ error, label, name, onChange, type = "text", values }) {
  return (
    <label className="room-field">
      <span>{label}</span>
      <input
        aria-invalid={Boolean(error)}
        name={name}
        onChange={(event) => onChange((current) => ({ ...current, [name]: event.target.value }))}
        step={name === "base_price" ? "0.01" : undefined}
        type={type}
        value={values[name] || ""}
      />
      {error ? <small>{Array.isArray(error) ? error[0] : error}</small> : null}
    </label>
  );
}
