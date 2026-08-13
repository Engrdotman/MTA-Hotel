import { X } from "lucide-react";
import { useEffect, useState } from "react";

import { getApiErrorMessage, idTypeOptions, mapValidationErrors } from "../guestUtils.js";

const emptyValues = {
  first_name: "",
  last_name: "",
  phone: "",
  email: "",
  address: "",
  id_type: "",
  id_number: "",
  nationality: "",
  date_of_birth: "",
  emergency_contact_name: "",
  emergency_contact_phone: "",
  notes: "",
};

export function GuestForm({ error, guest, isSubmitting, onClose, onSubmit }) {
  const [values, setValues] = useState(emptyValues);
  const [fieldErrors, setFieldErrors] = useState({});

  useEffect(() => {
    if (guest) {
      setValues({
        ...emptyValues,
        ...guest,
        date_of_birth: guest.date_of_birth || "",
      });
    } else {
      setValues(emptyValues);
    }
    setFieldErrors({});
  }, [guest]);

  useEffect(() => {
    setFieldErrors(mapValidationErrors(error));
  }, [error]);

  function updateField(event) {
    const { name, value } = event.target;
    setValues((current) => ({ ...current, [name]: value }));
    setFieldErrors((current) => ({ ...current, [name]: undefined }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmit(values);
  }

  return (
    <div aria-modal="true" className="guest-modal" role="dialog">
      <button aria-label="Close form" className="guest-modal-backdrop" onClick={onClose} type="button" />
      <form className="guest-form-panel" onSubmit={handleSubmit}>
        <div className="guest-modal-heading">
          <div>
            <h2>{guest ? "Edit Guest" : "Add Guest"}</h2>
            <p>{guest ? "Update guest information." : "Create a new hotel guest record."}</p>
          </div>
          <button aria-label="Close form" onClick={onClose} type="button">
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        {error && !Object.keys(fieldErrors).length ? (
          <p className="guest-form-error">{getApiErrorMessage(error)}</p>
        ) : null}

        <div className="guest-form-grid">
          <GuestField error={fieldErrors.first_name} label="First Name *" name="first_name" onChange={updateField} value={values.first_name} />
          <GuestField error={fieldErrors.last_name} label="Last Name *" name="last_name" onChange={updateField} value={values.last_name} />
          <GuestField error={fieldErrors.phone} label="Phone" name="phone" onChange={updateField} value={values.phone} />
          <GuestField error={fieldErrors.email} label="Email" name="email" onChange={updateField} type="email" value={values.email} />
          <GuestField label="Nationality" name="nationality" onChange={updateField} value={values.nationality} />
          <label className="guest-field">
            <span>ID Type</span>
            <select name="id_type" onChange={updateField} value={values.id_type}>
              <option value="">Select ID type</option>
              {idTypeOptions.map((option) => (
                <option key={option} value={option}>
                  {option.replace(/_/g, " ")}
                </option>
              ))}
            </select>
          </label>
          <GuestField label="ID Number" name="id_number" onChange={updateField} value={values.id_number} />
          <GuestField error={fieldErrors.date_of_birth} label="Date of Birth" name="date_of_birth" onChange={updateField} type="date" value={values.date_of_birth} />
          <GuestField label="Emergency Contact Name" name="emergency_contact_name" onChange={updateField} value={values.emergency_contact_name} />
          <GuestField error={fieldErrors.emergency_contact_phone} label="Emergency Contact Phone" name="emergency_contact_phone" onChange={updateField} value={values.emergency_contact_phone} />
          <GuestTextarea label="Address" name="address" onChange={updateField} value={values.address} />
          <GuestTextarea label="Notes" name="notes" onChange={updateField} value={values.notes} />
        </div>

        <div className="guest-form-actions">
          <button onClick={onClose} type="button">
            Cancel
          </button>
          <button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Saving..." : "Save Guest"}
          </button>
        </div>
      </form>
    </div>
  );
}

function GuestField({ error, label, name, onChange, type = "text", value }) {
  return (
    <label className="guest-field">
      <span>{label}</span>
      <input aria-invalid={Boolean(error)} name={name} onChange={onChange} type={type} value={value || ""} />
      {error ? <small>{Array.isArray(error) ? error[0] : error}</small> : null}
    </label>
  );
}

function GuestTextarea({ label, name, onChange, value }) {
  return (
    <label className="guest-field guest-field-wide">
      <span>{label}</span>
      <textarea name={name} onChange={onChange} rows={3} value={value || ""} />
    </label>
  );
}
