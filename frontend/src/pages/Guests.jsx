import { Plus } from "lucide-react";
import { useCallback, useState } from "react";

import { GuestDeleteDialog } from "../features/guests/components/GuestDeleteDialog.jsx";
import { GuestDetails } from "../features/guests/components/GuestDetails.jsx";
import { GuestFilters } from "../features/guests/components/GuestFilters.jsx";
import { GuestForm } from "../features/guests/components/GuestForm.jsx";
import { GuestSearch } from "../features/guests/components/GuestSearch.jsx";
import { GuestTable } from "../features/guests/components/GuestTable.jsx";
import { useGuests } from "../features/guests/hooks/useGuests.js";
import { createGuest, deleteGuest, updateGuest } from "../features/guests/services/guestService.js";
import { getApiErrorMessage } from "../features/guests/guestUtils.js";
import "../styles/guests.css";

const pageSize = 20;

export function Guests() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({ nationality: "", idType: "" });
  const [formGuest, setFormGuest] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedGuest, setSelectedGuest] = useState(null);
  const [deleteGuestTarget, setDeleteGuestTarget] = useState(null);
  const [deleteError, setDeleteError] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [notice, setNotice] = useState("");

  const { count, error, guests, hasNext, hasPrevious, isLoading, retry } = useGuests({
    filters,
    page,
    pageSize,
    search,
  });

  const handleSearch = useCallback((value) => {
    setSearch(value);
    setPage(1);
  }, []);

  function handleFiltersChange(nextFilters) {
    setFilters(nextFilters);
    setPage(1);
  }

  function openCreateForm() {
    setFormGuest(null);
    setFormError(null);
    setIsFormOpen(true);
  }

  function openEditForm(guest) {
    setFormGuest(guest);
    setFormError(null);
    setIsFormOpen(true);
  }

  async function handleSubmit(values) {
    setIsSubmitting(true);
    setFormError(null);

    try {
      if (formGuest) {
        await updateGuest(formGuest.id, values);
        setNotice("Guest updated successfully.");
      } else {
        await createGuest(values);
        setNotice("Guest created successfully.");
      }
      setIsFormOpen(false);
      await retry();
    } catch (requestError) {
      setFormError(requestError);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete() {
    if (!deleteGuestTarget) {
      return;
    }

    setIsDeleting(true);
    setDeleteError("");

    try {
      await deleteGuest(deleteGuestTarget.id);
      setDeleteGuestTarget(null);
      setNotice("Guest removed successfully.");
      await retry();
    } catch (requestError) {
      setDeleteError(getApiErrorMessage(requestError));
    } finally {
      setIsDeleting(false);
    }
  }

  const start = count === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, count);
  const isFiltered = Boolean(search || filters.nationality || filters.idType);

  return (
    <main className="dashboard-page guests-page">
      <section className="guests-header">
        <div>
          <p className="dashboard-kicker">Guest Management</p>
          <h2>Guests</h2>
          <p>Manage hotel guests and their information.</p>
        </div>
        <button className="guests-primary-button" onClick={openCreateForm} type="button">
          <Plus aria-hidden="true" size={18} />
          Add Guest
        </button>
      </section>

      {notice ? (
        <div className="dashboard-notice" role="status">
          {notice}
        </div>
      ) : null}

      <section className="dashboard-card guests-card">
        <div className="guests-toolbar">
          <GuestSearch onSearch={handleSearch} value={search} />
          <GuestFilters
            filters={filters}
            onChange={handleFiltersChange}
            onClear={() => handleFiltersChange({ nationality: "", idType: "" })}
          />
        </div>

        {error ? (
          <div className="guest-load-state">
            <p>Unable to load guests. Please try again.</p>
            <button onClick={retry} type="button">
              Retry
            </button>
          </div>
        ) : isLoading ? (
          <div className="guest-load-state">Loading guests...</div>
        ) : (
          <GuestTable
            guests={guests}
            isFiltered={isFiltered}
            onDelete={setDeleteGuestTarget}
            onEdit={openEditForm}
            onView={setSelectedGuest}
          />
        )}

        <div className="guests-pagination">
          <p>
            Showing {start}-{end} of {count} guests
          </p>
          <div>
            <button disabled={!hasPrevious || isLoading} onClick={() => setPage((current) => Math.max(1, current - 1))} type="button">
              Previous
            </button>
            <span>Page {page}</span>
            <button disabled={!hasNext || isLoading} onClick={() => setPage((current) => current + 1)} type="button">
              Next
            </button>
          </div>
        </div>
      </section>

      {isFormOpen ? (
        <GuestForm
          error={formError}
          guest={formGuest}
          isSubmitting={isSubmitting}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleSubmit}
        />
      ) : null}
      <GuestDetails guest={selectedGuest} onClose={() => setSelectedGuest(null)} />
      <GuestDeleteDialog
        error={deleteError}
        guest={deleteGuestTarget}
        isDeleting={isDeleting}
        onCancel={() => setDeleteGuestTarget(null)}
        onConfirm={handleDelete}
      />
    </main>
  );
}
