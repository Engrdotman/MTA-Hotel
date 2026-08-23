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
          <h2>Recent Bookings</h2>
          <p>Latest bookings from the front desk.</p>
        </div>
      </div>

      <DataTable columns={columns} rows={reservations} />
    </section>
  );
}
