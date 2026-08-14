import { CalendarDays, CheckCircle2, ClipboardList, Eye, Pencil, Plus, Search, Trash2, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { useReservations } from "../features/reservations/hooks/useReservations.js";
import {
  formatDate,
  formatReservationLabel,
  getApiErrorMessage,
  mapValidationErrors,
  reservationSourceOptions,
  reservationStatusOptions,
} from "../features/reservations/reservationUtils.js";
import {
  createReservation,
  deleteReservation,
  updateReservation,
  updateReservationStatus,
} from "../features/reservations/services/reservationService.js";
import "../styles/reservations.css";

const pageSize = 20;

export function Reservations() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({ status: "", room: "", guest: "", dateFrom: "", dateTo: "" });
  const [formReservation, setFormReservation] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [notice, setNotice] = useState("");

  const {
    count,
    error,
    guests,
    hasNext,
    hasPrevious,
    isLoading,
    reservations,
    retry,
    rooms,
    summary,
  } = useReservations({ filters, page, pageSize, search });

  const guestOptions = useMemo(
    () => guests.map((guest) => ({ label: `${guest.first_name} ${guest.last_name} (${guest.guest_code})`, value: String(guest.id) })),
    [guests],
  );
  const roomOptions = useMemo(
    () => rooms.map((room) => ({ label: `${room.room_number} - ${room.room_type_name}`, value: String(room.id) })),
    [rooms],
  );

  const handleSearch = useCallback((event) => {
    setSearch(event.target.value);
    setPage(1);
  }, []);

  function updateFilter(name, value) {
    setFilters((current) => ({ ...current, [name]: value }));
    setPage(1);
  }

  function openCreateForm() {
    setFormReservation(null);
    setFormError(null);
    setIsFormOpen(true);
  }

  function openEditForm(reservation) {
    setFormReservation(reservation);
    setFormError(null);
    setIsFormOpen(true);
  }

  async function handleSubmit(values) {
    setIsSubmitting(true);
    setFormError(null);

    try {
      if (formReservation) {
        await updateReservation(formReservation.id, values);
        setNotice("Reservation updated successfully.");
      } else {
        await createReservation(values);
        setNotice("Reservation created successfully.");
      }
      setIsFormOpen(false);
      await retry();
    } catch (requestError) {
      setFormError(requestError);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(reservation) {
    const confirmed = window.confirm(`Delete reservation ${reservation.reservation_number}?`);
    if (!confirmed) {
      return;
    }

    try {
      await deleteReservation(reservation.id);
      setNotice("Reservation removed successfully.");
      await retry();
    } catch (requestError) {
      setNotice(getApiErrorMessage(requestError));
    }
  }

  async function handleStatusChange(reservation, status) {
    try {
      await updateReservationStatus(reservation.id, status);
      setNotice("Reservation status updated successfully.");
      await retry();
    } catch (requestError) {
      setNotice(getApiErrorMessage(requestError));
    }
  }

  const start = count === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, count);
  const isFiltered = Boolean(search || filters.status || filters.room || filters.guest || filters.dateFrom || filters.dateTo);

  return (
    <main className="dashboard-page reservations-page">
      <section className="reservations-header">
        <div>
          <p className="dashboard-kicker">Reservation Management</p>
          <h2>Reservations</h2>
          <p>Create bookings, assign rooms, track guests, and move reservations through their stay lifecycle.</p>
        </div>
        <button className="reservations-primary-button" onClick={openCreateForm} type="button">
          <Plus aria-hidden="true" size={18} />
          New Reservation
        </button>
      </section>

      <section className="reservations-stats" aria-label="Reservation status summary">
        <ReservationStat icon={<ClipboardList aria-hidden="true" size={20} />} label="Total" value={summary.total} />
        <ReservationStat icon={<CalendarDays aria-hidden="true" size={20} />} label="Pending" tone="warning" value={summary.pending} />
        <ReservationStat icon={<CheckCircle2 aria-hidden="true" size={20} />} label="Confirmed" tone="info" value={summary.confirmed} />
        <ReservationStat icon={<CheckCircle2 aria-hidden="true" size={20} />} label="Checked In" tone="success" value={summary.checked_in} />
      </section>

      {notice ? (
        <div className="dashboard-notice" role="status">
          {notice}
        </div>
      ) : null}

      <section className="dashboard-card reservations-card">
        <div className="reservation-toolbar">
          <label className="reservation-search">
            <Search aria-hidden="true" size={18} />
            <input onChange={handleSearch} placeholder="Search reservation, guest, or room" type="search" value={search} />
          </label>
          <div className="reservation-filters">
            <label>
              Status
              <select onChange={(event) => updateFilter("status", event.target.value)} value={filters.status}>
                <option value="">All</option>
                {reservationStatusOptions.map((status) => (
                  <option key={status} value={status}>
                    {formatReservationLabel(status)}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Room
              <select onChange={(event) => updateFilter("room", event.target.value)} value={filters.room}>
                <option value="">All</option>
                {roomOptions.map((room) => (
                  <option key={room.value} value={room.value}>
                    {room.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Guest
              <select onChange={(event) => updateFilter("guest", event.target.value)} value={filters.guest}>
                <option value="">All</option>
                {guestOptions.map((guest) => (
                  <option key={guest.value} value={guest.value}>
                    {guest.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              From
              <input onChange={(event) => updateFilter("dateFrom", event.target.value)} type="date" value={filters.dateFrom} />
            </label>
            <label>
              To
              <input onChange={(event) => updateFilter("dateTo", event.target.value)} type="date" value={filters.dateTo} />
            </label>
            <button onClick={() => setFilters({ status: "", room: "", guest: "", dateFrom: "", dateTo: "" })} type="button">
              Clear
            </button>
          </div>
        </div>

        {error ? (
          <div className="reservation-load-state">
            <p>Unable to load reservations. Please try again.</p>
            <button onClick={retry} type="button">
              Retry
            </button>
          </div>
        ) : isLoading ? (
          <div className="reservation-load-state">Loading reservations...</div>
        ) : (
          <ReservationTable
            isFiltered={isFiltered}
            onDelete={handleDelete}
            onEdit={openEditForm}
            onStatusChange={handleStatusChange}
            onView={setSelectedReservation}
            reservations={reservations}
          />
        )}

        <div className="reservations-pagination">
          <p>
            Showing {start}-{end} of {count} reservations
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
        <ReservationForm
          error={formError}
          guestOptions={guestOptions}
          isSubmitting={isSubmitting}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleSubmit}
          reservation={formReservation}
          roomOptions={roomOptions}
        />
      ) : null}
      <ReservationDetails onClose={() => setSelectedReservation(null)} reservation={selectedReservation} />
    </main>
  );
}

function ReservationStat({ icon, label, tone = "default", value }) {
  return (
    <article className={`reservation-stat reservation-stat-${tone}`}>
      <div>{icon}</div>
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}

function ReservationTable({ isFiltered, onDelete, onEdit, onStatusChange, onView, reservations }) {
  if (!reservations.length) {
    return <div className="reservation-empty">{isFiltered ? "No reservations match these filters." : "No reservations yet."}</div>;
  }

  return (
    <div className="reservation-table-wrap">
      <table className="reservation-table">
        <thead>
          <tr>
            <th>Reservation</th>
            <th>Guest</th>
            <th>Room</th>
            <th>Dates</th>
            <th>Status</th>
            <th>Source</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {reservations.map((reservation) => (
            <tr key={reservation.id}>
              <td>
                <strong>{reservation.reservation_number}</strong>
                <span>{reservation.nights} night(s)</span>
              </td>
              <td>{reservation.guest_name}</td>
              <td>{reservation.room_number}</td>
              <td>
                {formatDate(reservation.check_in_date)} - {formatDate(reservation.check_out_date)}
              </td>
              <td>
                <select
                  className={`reservation-status-select reservation-status-${reservation.status.toLowerCase()}`}
                  onChange={(event) => onStatusChange(reservation, event.target.value)}
                  value={reservation.status}
                >
                  {reservationStatusOptions.map((status) => (
                    <option key={status} value={status}>
                      {formatReservationLabel(status)}
                    </option>
                  ))}
                </select>
              </td>
              <td>{reservation.source_display}</td>
              <td>
                <div className="reservation-actions">
                  <button aria-label={`View ${reservation.reservation_number}`} onClick={() => onView(reservation)} title="View" type="button">
                    <Eye aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Edit ${reservation.reservation_number}`} onClick={() => onEdit(reservation)} title="Edit" type="button">
                    <Pencil aria-hidden="true" size={16} />
                  </button>
                  <button aria-label={`Delete ${reservation.reservation_number}`} onClick={() => onDelete(reservation)} title="Delete" type="button">
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

function ReservationForm({ error, guestOptions, isSubmitting, onClose, onSubmit, reservation, roomOptions }) {
  const [values, setValues] = useState(() => getReservationFormValues(reservation));
  const errors = mapValidationErrors(error);
  const message = error ? getApiErrorMessage(error) : "";

  useEffect(() => {
    setValues(getReservationFormValues(reservation));
  }, [reservation]);

  function updateValue(name, value) {
    setValues((current) => {
      if (name === "guest") {
        return {
          ...current,
          guest: value,
          additional_guest_ids: current.additional_guest_ids.filter((guestId) => guestId !== value),
        };
      }
      return { ...current, [name]: value };
    });
  }

  function submit(event) {
    event.preventDefault();
    onSubmit({
      ...values,
      guest: Number(values.guest),
      room: Number(values.room),
      adults: Number(values.adults),
      children: Number(values.children),
      additional_guest_ids: values.additional_guest_ids.map(Number),
    });
  }

  return (
    <div className="reservation-modal" role="dialog" aria-modal="true">
      <button aria-label="Close reservation form" className="reservation-modal-backdrop" onClick={onClose} type="button" />
      <form className="reservation-panel" onSubmit={submit}>
        <div className="reservation-modal-heading">
          <div>
            <p className="dashboard-kicker">{reservation ? "Edit Reservation" : "New Reservation"}</p>
            <h2>{reservation ? reservation.reservation_number : "Create reservation"}</h2>
          </div>
          <button aria-label="Close" onClick={onClose} type="button">
            <X aria-hidden="true" size={18} />
          </button>
        </div>

        {message ? <div className="reservation-form-error">{message}</div> : null}

        <div className="reservation-form-grid">
          <Field error={errors.guest} label="Guest">
            <select required onChange={(event) => updateValue("guest", event.target.value)} value={values.guest}>
              <option value="">Select guest</option>
              {guestOptions.map((guest) => (
                <option key={guest.value} value={guest.value}>
                  {guest.label}
                </option>
              ))}
            </select>
          </Field>
          <Field error={errors.room} label="Room">
            <select required onChange={(event) => updateValue("room", event.target.value)} value={values.room}>
              <option value="">Select room</option>
              {roomOptions.map((room) => (
                <option key={room.value} value={room.value}>
                  {room.label}
                </option>
              ))}
            </select>
          </Field>
          <Field error={errors.check_in_date} label="Check-in">
            <input required onChange={(event) => updateValue("check_in_date", event.target.value)} type="date" value={values.check_in_date} />
          </Field>
          <Field error={errors.check_out_date} label="Check-out">
            <input required onChange={(event) => updateValue("check_out_date", event.target.value)} type="date" value={values.check_out_date} />
          </Field>
          <Field error={errors.adults} label="Adults">
            <input min="1" onChange={(event) => updateValue("adults", event.target.value)} type="number" value={values.adults} />
          </Field>
          <Field error={errors.children} label="Children">
            <input min="0" onChange={(event) => updateValue("children", event.target.value)} type="number" value={values.children} />
          </Field>
          <Field error={errors.additional_guest_ids} label="Additional Guests">
            <select
              multiple
              onChange={(event) =>
                updateValue(
                  "additional_guest_ids",
                  Array.from(event.target.selectedOptions, (option) => option.value),
                )
              }
              value={values.additional_guest_ids}
            >
              {guestOptions
                .filter((guest) => guest.value !== String(values.guest))
                .map((guest) => (
                  <option key={guest.value} value={guest.value}>
                    {guest.label}
                  </option>
                ))}
            </select>
          </Field>
          <Field error={errors.status} label="Status">
            <select onChange={(event) => updateValue("status", event.target.value)} value={values.status}>
              {reservationStatusOptions.map((status) => (
                <option key={status} value={status}>
                  {formatReservationLabel(status)}
                </option>
              ))}
            </select>
          </Field>
          <Field error={errors.source} label="Source">
            <select onChange={(event) => updateValue("source", event.target.value)} value={values.source}>
              {reservationSourceOptions.map((source) => (
                <option key={source} value={source}>
                  {formatReservationLabel(source)}
                </option>
              ))}
            </select>
          </Field>
          <Field className="reservation-field-wide" error={errors.special_requests} label="Special Requests">
            <textarea onChange={(event) => updateValue("special_requests", event.target.value)} value={values.special_requests} />
          </Field>
          <Field className="reservation-field-wide" error={errors.notes} label="Notes">
            <textarea onChange={(event) => updateValue("notes", event.target.value)} value={values.notes} />
          </Field>
        </div>

        <div className="reservation-form-actions">
          <button onClick={onClose} type="button">
            Cancel
          </button>
          <button disabled={isSubmitting} type="submit">
            {isSubmitting ? "Saving..." : "Save Reservation"}
          </button>
        </div>
      </form>
    </div>
  );
}

function getReservationFormValues(reservation) {
  return {
    guest: reservation?.guest ? String(reservation.guest) : "",
    room: reservation?.room ? String(reservation.room) : "",
    check_in_date: reservation?.check_in_date || "",
    check_out_date: reservation?.check_out_date || "",
    adults: reservation?.adults || 1,
    children: reservation?.children || 0,
    status: reservation?.status || "PENDING",
    source: reservation?.source || "WALK_IN",
    additional_guest_ids: reservation?.additional_guests?.map((guest) => String(guest.id)) || [],
    special_requests: reservation?.special_requests || "",
    notes: reservation?.notes || "",
  };
}

function Field({ children, className = "", error, label }) {
  return (
    <label className={`reservation-field ${className}`}>
      {label}
      {children}
      {error ? <small>{Array.isArray(error) ? error.join(" ") : error}</small> : null}
    </label>
  );
}

function ReservationDetails({ onClose, reservation }) {
  if (!reservation) {
    return null;
  }

  return (
    <aside className="reservation-drawer" role="dialog" aria-modal="true">
      <button aria-label="Close reservation details" className="reservation-modal-backdrop" onClick={onClose} type="button" />
      <div className="reservation-drawer-panel">
        <div className="reservation-modal-heading">
          <div>
            <p className="dashboard-kicker">Reservation Details</p>
            <h2>{reservation.reservation_number}</h2>
          </div>
          <button aria-label="Close" onClick={onClose} type="button">
            <X aria-hidden="true" size={18} />
          </button>
        </div>
        <dl className="reservation-details-list">
          <Detail label="Guest" value={`${reservation.guest_name} (${reservation.guest_code})`} />
          <Detail label="Room" value={`${reservation.room_number} - ${reservation.room_type_name}`} />
          <Detail label="Dates" value={`${formatDate(reservation.check_in_date)} - ${formatDate(reservation.check_out_date)}`} />
          <Detail label="Occupancy" value={`${reservation.adults} adult(s), ${reservation.children} child(ren)`} />
          <Detail label="Status" value={reservation.status_display} />
          <Detail label="Source" value={reservation.source_display} />
          <Detail
            label="Additional Guests"
            value={
              reservation.additional_guests?.length
                ? reservation.additional_guests.map((guest) => guest.full_name || `${guest.first_name} ${guest.last_name}`).join(", ")
                : "-"
            }
          />
          <Detail label="Special Requests" value={reservation.special_requests || "-"} />
          <Detail label="Notes" value={reservation.notes || "-"} />
        </dl>
      </div>
    </aside>
  );
}

function Detail({ label, value }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}
