import { X } from "lucide-react";
import { useEffect, useState } from "react";

import { getApiErrorMessage, mapValidationErrors } from "../../rooms/roomUtils.js";

const roleOptions = [
  ["MANAGER", "Manager"],
  ["RECEPTIONIST", "Receptionist"],
  ["ACCOUNTANT", "Accountant"],
  ["STAFF", "Staff"],
];

const initialValues = {
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  role: "STAFF",
  temporary_password: "",
  confirm_password: "",
  is_active: true,
};

export function UserForm({ error, isSubmitting, onClose, onSubmit, user }) {
  const [values, setValues] = useState(initialValues);
  const validationErrors = mapValidationErrors(error);
  const isEditing = Boolean(user);

  useEffect(() => {
    if (user) {
      setValues({
        first_name: user.first_name ?? "",
        last_name: user.last_name ?? "",
        email: user.email ?? "",
        phone: user.phone ?? "",
        role: user.role ?? "STAFF",
        temporary_password: "",
        confirm_password: "",
        is_active: Boolean(user.is_active),
      });
      return;
    }

    setValues(initialValues);
  }, [user]);

  function updateField(field, value) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const payload = { ...values };
    if (isEditing) {
      delete payload.email;
      delete payload.temporary_password;
      delete payload.confirm_password;
      if (user.role === "ADMIN") {
        delete payload.role;
      }
    }
    onSubmit(payload);
  }

  return (
    <div aria-modal="true" className="room-modal" role="dialog">
      <button aria-label="Close user form" className="room-modal-backdrop" onClick={onClose} type="button" />
      <form className="room-panel user-form" onSubmit={handleSubmit}>
        <div className="room-modal-heading">
          <div>
            <p className="dashboard-kicker">User Management</p>
            <h2>{isEditing ? "Edit User" : "Add User"}</h2>
          </div>
          <button aria-label="Close user form" onClick={onClose} type="button">
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        {error ? <div className="dashboard-error">{getApiErrorMessage(error)}</div> : null}

        <div className="room-form-grid">
          <label className="room-field">
            First Name
            <input value={values.first_name} onChange={(event) => updateField("first_name", event.target.value)} required />
            {validationErrors.first_name ? <span>{validationErrors.first_name}</span> : null}
          </label>
          <label className="room-field">
            Last Name
            <input value={values.last_name} onChange={(event) => updateField("last_name", event.target.value)} required />
            {validationErrors.last_name ? <span>{validationErrors.last_name}</span> : null}
          </label>
          <label className="room-field">
            Email
            <input disabled={isEditing} type="email" value={values.email} onChange={(event) => updateField("email", event.target.value)} required />
            {validationErrors.email ? <span>{validationErrors.email}</span> : null}
          </label>
          <label className="room-field">
            Phone
            <input value={values.phone} onChange={(event) => updateField("phone", event.target.value)} />
            {validationErrors.phone ? <span>{validationErrors.phone}</span> : null}
          </label>
          <label className="room-field">
            Role
            <select disabled={user?.role === "ADMIN"} value={values.role} onChange={(event) => updateField("role", event.target.value)}>
              {user?.role === "ADMIN" ? <option value="ADMIN">Admin</option> : null}
              {roleOptions.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
            {validationErrors.role ? <span>{validationErrors.role}</span> : null}
          </label>
          <label className="room-field user-active-field">
            Status
            <select value={String(values.is_active)} onChange={(event) => updateField("is_active", event.target.value === "true")}>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </label>
          {!isEditing ? (
            <>
              <label className="room-field">
                Temporary Password
                <input type="password" value={values.temporary_password} onChange={(event) => updateField("temporary_password", event.target.value)} required />
                {validationErrors.temporary_password ? <span>{validationErrors.temporary_password}</span> : null}
              </label>
              <label className="room-field">
                Confirm Password
                <input type="password" value={values.confirm_password} onChange={(event) => updateField("confirm_password", event.target.value)} required />
                {validationErrors.confirm_password ? <span>{validationErrors.confirm_password}</span> : null}
              </label>
            </>
          ) : null}
        </div>

        <div className="room-form-actions">
          <button onClick={onClose} type="button">Cancel</button>
          <button disabled={isSubmitting} type="submit">{isSubmitting ? "Saving..." : "Save User"}</button>
        </div>
      </form>
    </div>
  );
}
