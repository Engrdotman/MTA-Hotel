import { X } from "lucide-react";

import { Sidebar } from "./Sidebar.jsx";

export function MobileSidebar({ isOpen, onClose, onLogout, user }) {
  return (
    <div className={`mobile-sidebar ${isOpen ? "mobile-sidebar-open" : ""}`}>
      <button
        aria-label="Close menu"
        className="mobile-sidebar-backdrop"
        onClick={onClose}
        type="button"
      />
      <div className="mobile-sidebar-panel">
        <button aria-label="Close menu" className="mobile-sidebar-close" onClick={onClose} type="button">
          <X aria-hidden="true" size={20} />
        </button>
        <Sidebar onLogout={onLogout} onNavigate={onClose} user={user} />
      </div>
    </div>
  );
}
