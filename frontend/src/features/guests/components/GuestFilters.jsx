import { idTypeOptions } from "../guestUtils.js";

export function GuestFilters({ filters, onChange, onClear }) {
  return (
    <div className="guest-filters">
      <label>
        <span>Nationality</span>
        <input
          onChange={(event) => onChange({ ...filters, nationality: event.target.value })}
          placeholder="Any nationality"
          value={filters.nationality}
        />
      </label>

      <label>
        <span>ID Type</span>
        <select
          onChange={(event) => onChange({ ...filters, idType: event.target.value })}
          value={filters.idType}
        >
          <option value="">Any ID type</option>
          {idTypeOptions.map((option) => (
            <option key={option} value={option}>
              {option.replace(/_/g, " ")}
            </option>
          ))}
        </select>
      </label>

      <button onClick={onClear} type="button">
        Clear Filters
      </button>
    </div>
  );
}
