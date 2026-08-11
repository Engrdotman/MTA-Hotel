export function PlaceholderPage({ title }) {
  return (
    <main className="dashboard-page">
      <section className="dashboard-card placeholder-card">
        <p className="dashboard-kicker">Coming soon</p>
        <h2>{title}</h2>
        <p>This module placeholder keeps navigation ready without implementing functionality yet.</p>
      </section>
    </main>
  );
}
