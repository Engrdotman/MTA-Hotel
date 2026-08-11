import { CalendarDays } from "lucide-react";
import { useState } from "react";

import { QuickActions } from "../components/dashboard/QuickActions.jsx";
import { RecentReservations } from "../components/dashboard/RecentReservations.jsx";
import { RoomStatusOverview } from "../components/dashboard/RoomStatusOverview.jsx";
import { StatCard } from "../components/dashboard/StatCard.jsx";
import { recentReservations, roomStatus, statCards } from "../data/dashboardMock.js";
import { useAuth } from "../features/auth/authContext.js";

export function Dashboard() {
  const { user } = useAuth();
  const [notice, setNotice] = useState("");
  const firstName = user?.first_name || user?.email || "there";

  function handleQuickAction(label) {
    setNotice(`${label} will be available when the module is implemented.`);
  }

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
          <span>Tuesday, 11 Aug 2026</span>
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

      <RecentReservations reservations={recentReservations} />
    </main>
  );
}
