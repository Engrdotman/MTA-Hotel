import { Search } from "lucide-react";
import { useEffect, useState } from "react";

export function GuestSearch({ onSearch, value }) {
  const [draft, setDraft] = useState(value);

  useEffect(() => {
    setDraft(value);
  }, [value]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      onSearch(draft.trim());
    }, 350);

    return () => window.clearTimeout(timer);
  }, [draft, onSearch]);

  return (
    <label className="guest-search">
      <Search aria-hidden="true" size={18} />
      <span className="sr-only">Search guests</span>
      <input
        onChange={(event) => setDraft(event.target.value)}
        placeholder="Search guests..."
        type="search"
        value={draft}
      />
    </label>
  );
}
