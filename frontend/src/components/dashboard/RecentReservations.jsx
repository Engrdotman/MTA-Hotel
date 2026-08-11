import { DataTable } from "./DataTable.jsx";

const columns = [
  { key: "guest", label: "Guest" },
  { key: "room", label: "Room" },
  { key: "checkIn", label: "Check-in" },
  { key: "checkOut", label: "Check-out" },
  {
    key: "status",
    label: "Status",
    render: (status) => <span className={`status-pill status-${status.toLowerCase().replace(/\s+/g, "-")}`}>{status}</span>,
  },
];

export function RecentReservations({ reservations }) {
  return (
    <section className="dashboard-card reservations-card">
      <div className="card-heading card-heading-row">
        <div>
          <h2>Recent Reservations</h2>
          <p>Frontend mock data for today's desk review.</p>
        </div>
        <span className="mock-label">Mock data</span>
      </div>

      <DataTable columns={columns} rows={reservations} />
    </section>
  );
}
