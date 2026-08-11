const totalRooms = 24;

export function RoomStatusOverview({ statuses }) {
  if (!statuses.length) {
    return (
      <section className="dashboard-card room-overview">
        <div className="card-heading">
          <h2>Room Overview</h2>
          <p>No room status data available.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="dashboard-card room-overview">
      <div className="card-heading">
        <h2>Room Overview</h2>
        <p>Live room mix for today.</p>
      </div>

      <div className="room-status-list">
        {statuses.map((status) => {
          const percentage = Math.round((status.value / totalRooms) * 100);

          return (
            <div className="room-status-row" key={status.label}>
              <div>
                <span>{status.label}</span>
                <strong>{status.value}</strong>
              </div>
              <div className="room-progress" aria-label={`${status.label}: ${percentage}%`}>
                <span className={`room-progress-fill room-progress-${status.tone}`} style={{ width: `${percentage}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
