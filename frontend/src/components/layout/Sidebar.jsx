import { LogOut } from "lucide-react";
import { NavLink } from "react-router-dom";

import { BrandLogo } from "../common/BrandLogo.jsx";
import { hasAnyRole } from "../../features/auth/authorization.js";
import { navigationSections } from "./navigation.js";

export function Sidebar({ collapsed = false, onLogout, onNavigate, user }) {
  const sections = navigationSections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => hasAnyRole(user, item.roles)),
    }))
    .filter((section) => section.items.length > 0);

  return (
    <aside className={`app-sidebar ${collapsed ? "app-sidebar-collapsed" : ""}`}>
      <div className="sidebar-brand">
        <BrandLogo compact={collapsed} showText={!collapsed} />
      </div>

      <nav className="sidebar-nav" aria-label="Dashboard navigation">
        {sections.map((section) => (
          <div className="sidebar-section" key={section.label}>
            {!collapsed ? <p>{section.label}</p> : null}
            {section.items.map((item) => (
              <NavLink
                className={({ isActive }) => `sidebar-link ${isActive ? "sidebar-link-active" : ""}`}
                key={item.path}
                onClick={onNavigate}
                to={item.path}
              >
                <item.icon aria-hidden="true" size={18} />
                {!collapsed ? <span>{item.label}</span> : null}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <button className="sidebar-link sidebar-logout" onClick={onLogout} type="button">
          <LogOut aria-hidden="true" size={18} />
          {!collapsed ? <span>Logout</span> : null}
        </button>
      </div>
    </aside>
  );
}
