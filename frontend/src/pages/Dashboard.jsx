import { CalendarDays } from "lucide-react";
import { useState } from "react";

import { QuickActions } from "../components/dashboard/QuickActions.jsx";
import { RecentReservations } from "../components/dashboard/RecentReservations.jsx";
import { RoomStatusOverview } from "../components/dashboard/RoomStatusOverview.jsx";
import { StatCard } from "../components/dashboard/StatCard.jsx";
import { useAuth } from "../features/auth/authContext.js";
import useDashboard from "../features/dashboard/useDashboard.js";

export function Dashboard() {
  const { user } = useAuth();
  const { dashboard, occupancy, reservations, loading, error } = useDashboard();
  const [notice, setNotice] = useState("");
  const firstName = user?.first_name || user?.email || "there";

  function handleQuickAction(label) {
    setNotice(`${label} will be available when the module is implemented.`);
  }

  if (error) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-error">
          <p>Error loading dashboard: {error}</p>
        </div>
      </main>
    );
  }

  if (loading) {
    return (
      <main className="dashboard-page">
        <div className="dashboard-loading">
          <p>Loading dashboard...</p>
        </div>
      </main>
    );
  }

  // Transform dashboard data into stat cards format
  const statCards = dashboard ? [
    {
      id: "total-rooms",
      label: "Total Rooms",
      value: dashboard.total_rooms || 0,
      support: `${dashboard.available_rooms || 0} available today`,
      tone: "primary",
    },
    {
      id: "occupied-rooms",
      label: "Occupied Rooms",
      value: dashboard.occupied_rooms || 0,
      support: occupancy ? `${occupancy.occupancy_rate || 0}% occupancy` : "0% occupancy",
      tone: "success",
    },
    {
      id: "check-ins",
      label: "Today's Check-ins",
      value: dashboard.today_check_ins || 0,
      support: `${dashboard.current_guests || 0} current guests`,
      tone: "info",
    },
    {
      id: "revenue",
      label: "Today's Revenue",
      value: dashboard.today_revenue || 0,
      support: "From payments received",
      tone: "warning",
      format: "currency",
    },
  ] : [];

  // Transform occupancy data into room status format
  const roomStatus = occupancy ? [
    { label: "Available", value: occupancy.available || 0, tone: "success" },
    { label: "Occupied", value: occupancy.occupied || 0, tone: "primary" },
    { label: "Reserved", value: occupancy.reserved || 0, tone: "info" },
    { label: "Maintenance", value: occupancy.maintenance || 0, tone: "warning" },
  ] : [];

  return (
    <main className="dashboard-page">
      <section className="dashboard-hero">
        <div>
          <p className="dashboard-kicker">Hotel command center</p>
          <h2>Good morning, {firstName}</h2>
          <p>Here's what's happening at M.T.A Hotel today.</p>
        </div>
        <div className="dashboard-date">
          <CalendarDays aria-hidden="true" size={18} />
          <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
        </div>
      </section>

      {notice ? (
        <div className="dashboard-notice" role="status">
          {notice}
        </div>
      ) : null}

      <section className="stat-grid" aria-label="Hotel summary">
        {statCards.map((stat) => (
          <StatCard key={stat.id} stat={stat} />
        ))}
      </section>

      <section className="dashboard-grid">
        <RoomStatusOverview statuses={roomStatus} />
        <QuickActions onAction={handleQuickAction} />
      </section>

      <RecentReservations reservations={reservations} />
    </main>
  );
}
