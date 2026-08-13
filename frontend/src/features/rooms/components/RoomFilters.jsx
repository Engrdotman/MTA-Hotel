import { Search } from "lucide-react";

import { formatStatus, roomStatuses } from "../roomUtils.js";

export function RoomFilters({ filters, onChange, onClear, onSearch, roomTypes, search }) {
  return (
    <div className="room-toolbar">
      <label className="room-search">
        <Search aria-hidden="true" size={18} />
        <span className="sr-only">Search rooms</span>
        <input
          onChange={(event) => onSearch(event.target.value)}
          placeholder="Search room number..."
          type="search"
          value={search}
        />
      </label>

      <div className="room-filters">
        <label>
          <span>Room Type</span>
          <select onChange={(event) => onChange({ ...filters, roomType: event.target.value })} value={filters.roomType}>
            <option value="">All room types</option>
            {roomTypes.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Status</span>
          <select onChange={(event) => onChange({ ...filters, status: event.target.value })} value={filters.status}>
            <option value="">All statuses</option>
            {roomStatuses.map((status) => (
              <option key={status} value={status}>
                {formatStatus(status)}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Floor</span>
          <input
            onChange={(event) => onChange({ ...filters, floor: event.target.value })}
            placeholder="Any floor"
            value={filters.floor}
          />
        </label>
        <button onClick={onClear} type="button">
          Clear
        </button>
      </div>
    </div>
  );
}
