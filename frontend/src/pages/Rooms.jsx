import { BedDouble, Layers, Plus, Settings2, Sparkles } from "lucide-react";
import { useCallback, useState } from "react";

import { RoomDetails } from "../features/rooms/components/RoomDetails.jsx";
import { RoomFilters } from "../features/rooms/components/RoomFilters.jsx";
import { RoomForm } from "../features/rooms/components/RoomForm.jsx";
import { RoomStatusDialog } from "../features/rooms/components/RoomStatusDialog.jsx";
import { RoomTable } from "../features/rooms/components/RoomTable.jsx";
import { RoomTypeManager } from "../features/rooms/components/RoomTypeManager.jsx";
import { useRooms } from "../features/rooms/hooks/useRooms.js";
import {
  createRoom,
  deleteRoom,
  updateRoom,
  updateRoomStatus,
} from "../features/rooms/services/roomService.js";
import { getApiErrorMessage } from "../features/rooms/roomUtils.js";
import "../styles/rooms.css";

const pageSize = 20;

export function Rooms() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({ floor: "", roomType: "", status: "" });
  const [formRoom, setFormRoom] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formError, setFormError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [statusRoom, setStatusRoom] = useState(null);
  const [statusError, setStatusError] = useState("");
  const [isStatusSubmitting, setIsStatusSubmitting] = useState(false);
  const [isTypeManagerOpen, setIsTypeManagerOpen] = useState(false);
  const [notice, setNotice] = useState("");

  const {
    count,
    error,
    hasNext,
    hasPrevious,
    isLoading,
    retry,
    rooms,
    roomTypes,
    summary,
  } = useRooms({
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
    setFormRoom(null);
    setFormError(null);
    setIsFormOpen(true);
  }

  function openEditForm(room) {
    setFormRoom(room);
    setFormError(null);
    setIsFormOpen(true);
  }

  async function handleSubmit(values) {
    setIsSubmitting(true);
    setFormError(null);

    try {
      if (formRoom) {
        await updateRoom(formRoom.id, values);
        setNotice("Room updated successfully.");
      } else {
        await createRoom(values);
        setNotice("Room created successfully.");
      }
      setIsFormOpen(false);
      await retry();
    } catch (requestError) {
      setFormError(requestError);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(room) {
    const confirmed = window.confirm(`Delete room ${room.room_number}?`);

    if (!confirmed) {
      return;
    }

    try {
      await deleteRoom(room.id);
      setNotice("Room removed successfully.");
      await retry();
    } catch (requestError) {
      setNotice(getApiErrorMessage(requestError));
    }
  }

  async function handleStatusChange(status) {
    if (!statusRoom) {
      return;
    }

    setIsStatusSubmitting(true);
    setStatusError("");

    try {
      await updateRoomStatus(statusRoom.id, status);
      setStatusRoom(null);
      setNotice("Room status updated successfully.");
      await retry();
    } catch (requestError) {
      setStatusError(getApiErrorMessage(requestError));
    } finally {
      setIsStatusSubmitting(false);
    }
  }

  const start = count === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, count);
  const isFiltered = Boolean(search || filters.floor || filters.roomType || filters.status);

  return (
    <main className="dashboard-page rooms-page">
      <section className="rooms-header">
        <div>
          <p className="dashboard-kicker">Room Management</p>
          <h2>Rooms</h2>
          <p>Manage room inventory, room types, pricing, and operating status.</p>
        </div>
        <div className="rooms-header-actions">
          <button className="rooms-secondary-button" onClick={() => setIsTypeManagerOpen(true)} type="button">
            <Settings2 aria-hidden="true" size={18} />
            Room Types
          </button>
          <button className="rooms-primary-button" onClick={openCreateForm} type="button">
            <Plus aria-hidden="true" size={18} />
            Add Room
          </button>
        </div>
      </section>

      <section className="rooms-stats" aria-label="Room status summary">
        <RoomStat icon={<BedDouble aria-hidden="true" size={20} />} label="Total Rooms" value={summary.total} />
        <RoomStat icon={<Sparkles aria-hidden="true" size={20} />} label="Available" tone="success" value={summary.available} />
        <RoomStat icon={<Layers aria-hidden="true" size={20} />} label="Occupied" tone="primary" value={summary.occupied} />
        <RoomStat icon={<BedDouble aria-hidden="true" size={20} />} label="Reserved" tone="info" value={summary.reserved} />
      </section>

      {notice ? (
        <div className="dashboard-notice" role="status">
          {notice}
        </div>
      ) : null}

      <section className="dashboard-card rooms-card">
        <RoomFilters
          filters={filters}
          onChange={handleFiltersChange}
          onClear={() => handleFiltersChange({ floor: "", roomType: "", status: "" })}
          onSearch={handleSearch}
          roomTypes={roomTypes}
          search={search}
        />

        {error ? (
          <div className="room-load-state">
            <p>Unable to load rooms. Please try again.</p>
            <button onClick={retry} type="button">
              Retry
            </button>
          </div>
        ) : isLoading ? (
          <div className="room-load-state">Loading rooms...</div>
        ) : (
          <RoomTable
            isFiltered={isFiltered}
            onDelete={handleDelete}
            onEdit={openEditForm}
            onStatus={(room) => {
              setStatusError("");
              setStatusRoom(room);
            }}
            onView={setSelectedRoom}
            rooms={rooms}
          />
        )}

        <div className="rooms-pagination">
          <p>
            Showing {start}-{end} of {count} rooms
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
        <RoomForm
          error={formError}
          isSubmitting={isSubmitting}
          onClose={() => setIsFormOpen(false)}
          onSubmit={handleSubmit}
          room={formRoom}
          roomTypes={roomTypes}
        />
      ) : null}
      <RoomDetails onClose={() => setSelectedRoom(null)} room={selectedRoom} />
      <RoomStatusDialog
        error={statusError}
        isSubmitting={isStatusSubmitting}
        onCancel={() => setStatusRoom(null)}
        onConfirm={handleStatusChange}
        room={statusRoom}
      />
      <RoomTypeManager isOpen={isTypeManagerOpen} onChanged={retry} onClose={() => setIsTypeManagerOpen(false)} />
    </main>
  );
}

function RoomStat({ icon, label, tone = "default", value }) {
  return (
    <article className={`room-stat room-stat-${tone}`}>
      <div>{icon}</div>
      <p>{label}</p>
      <strong>{value}</strong>
    </article>
  );
}
