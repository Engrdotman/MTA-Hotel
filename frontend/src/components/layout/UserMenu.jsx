import { ChevronDown, LogOut, UserRound } from "lucide-react";
import { useState } from "react";

function getUserDisplay(user) {
  const firstName = user?.first_name || "";
  const lastName = user?.last_name || "";
  const fullName = `${firstName} ${lastName}`.trim() || user?.email || "User";
  const initials = `${firstName[0] || ""}${lastName[0] || ""}` || fullName.slice(0, 2);

  return {
    fullName,
    initials: initials.toUpperCase(),
    role: user?.role || "STAFF",
  };
}

export function UserMenu({ onLogout, user, variant = "topbar" }) {
  const [isOpen, setIsOpen] = useState(false);
  const display = getUserDisplay(user);

  return (
    <div className={`user-menu user-menu-${variant}`}>
      <button
        aria-expanded={isOpen}
        aria-haspopup="menu"
        className="user-menu-trigger"
        onClick={() => setIsOpen((current) => !current)}
        type="button"
      >
        <span className="user-avatar">{display.initials}</span>
        <span className="user-menu-copy">
          <strong>{display.fullName}</strong>
          <small>{display.role}</small>
        </span>
        <ChevronDown aria-hidden="true" size={16} />
      </button>

      {isOpen ? (
        <div className="user-menu-popover" role="menu">
          <button role="menuitem" type="button">
            <UserRound aria-hidden="true" size={16} />
            Profile
          </button>
          <button onClick={onLogout} role="menuitem" type="button">
            <LogOut aria-hidden="true" size={16} />
            Logout
          </button>
        </div>
      ) : null}
    </div>
  );
}
