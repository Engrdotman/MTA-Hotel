import { Plus } from "lucide-react";
import { useState } from "react";

import { UserDetails } from "../features/users/components/UserDetails.jsx";
import { UserForm } from "../features/users/components/UserForm.jsx";
import { UserTable } from "../features/users/components/UserTable.jsx";
import { useUsers } from "../features/users/hooks/useUsers.js";
import { createUser, deactivateUser, updateUser } from "../features/users/services/userService.js";
import { getApiErrorMessage } from "../features/rooms/roomUtils.js";
import "../styles/users.css";

export function Users() {
  const { error, isLoading, retry, users } = useUsers();
  const [formUser, setFormUser] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [notice, setNotice] = useState("");

  function openCreateForm() {
    setFormUser(null);
    setFormError(null);
    setIsFormOpen(true);
  }

  function openEditForm(user) {
    setFormUser(user);
    setFormError(null);
    setIsFormOpen(true);
  }

  async function handleSubmit(values) {
    setIsSubmitting(true);
    setFormError(null);

    try {
      if (formUser) {
        await updateUser(formUser.id, values);
        setNotice("User updated successfully.");
      } else {
        await createUser(values);
        setNotice("User created successfully.");
      }
      setIsFormOpen(false);
      await retry();
    } catch (requestError) {
      setFormError(requestError);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeactivate(user) {
    const confirmed = window.confirm(`Deactivate ${user.email}?`);
    if (!confirmed) {
      return;
    }

    try {
      await deactivateUser(user.id);
      setNotice("User deactivated successfully.");
      await retry();
    } catch (requestError) {
      setNotice(getApiErrorMessage(requestError));
    }
  }

  return (
    <main className="dashboard-page users-page">
      <section className="rooms-header">
        <div>
          <p className="dashboard-kicker">Settings</p>
          <h2>Users</h2>
          <p>Manage staff accounts, roles, and account status.</p>
        </div>
        <button className="rooms-primary-button" onClick={openCreateForm} type="button">
          <Plus aria-hidden="true" size={18} />
          Add User
        </button>
      </section>

      {notice ? <div className="dashboard-notice" role="status">{notice}</div> : null}

      <section className="dashboard-card rooms-card">
        {error ? (
          <div className="room-load-state">
            <p>{getApiErrorMessage(error)}</p>
            <button onClick={retry} type="button">Retry</button>
          </div>
        ) : isLoading ? (
          <div className="room-load-state">Loading users...</div>
        ) : (
          <UserTable
            onDeactivate={handleDeactivate}
            onEdit={openEditForm}
            onView={setSelectedUser}
            users={users}
          />
        )}
      </section>

      {isFormOpen ? (
        <UserForm
          error={formError}
          isSubmitting={isSubmitting}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleSubmit}
          user={formUser}
        />
      ) : null}
      <UserDetails onClose={() => setSelectedUser(null)} user={selectedUser} />
    </main>
  );
}
