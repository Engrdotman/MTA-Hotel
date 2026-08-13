import { useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";

import { MobileSidebar } from "../components/layout/MobileSidebar.jsx";
import { Sidebar } from "../components/layout/Sidebar.jsx";
import { Topbar } from "../components/layout/Topbar.jsx";
import { useAuth } from "../features/auth/authContext.js";
import "../styles/dashboard.css";

export function DashboardLayout() {
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <Sidebar onLogout={handleLogout} user={user} />
      <MobileSidebar
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        onLogout={handleLogout}
        user={user}
      />
      <div className="app-main">
        <Topbar
          onMenuClick={() => setIsMobileMenuOpen(true)}
          onLogout={handleLogout}
          title="Dashboard"
          user={user}
        />
        <Outlet />
      </div>
    </div>
  );
}
