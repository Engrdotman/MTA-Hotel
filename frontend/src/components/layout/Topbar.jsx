import { Bell, Menu } from "lucide-react";

import { UserMenu } from "./UserMenu.jsx";

export function Topbar({ onLogout, onMenuClick, title, user }) {
  return (
    <header className="app-topbar">
      <button aria-label="Open menu" className="topbar-menu-button" onClick={onMenuClick} type="button">
        <Menu aria-hidden="true" size={21} />
      </button>

      <div className="topbar-title">
        <h1>{title}</h1>
        <p>M.T.A Hotel operations desk</p>
      </div>

      <div className="topbar-actions">
        <button aria-label="Notifications" className="topbar-icon-button" type="button">
          <Bell aria-hidden="true" size={19} />
          <span aria-hidden="true" />
        </button>
        <UserMenu onLogout={onLogout} user={user} />
      </div>
    </header>
  );
}
