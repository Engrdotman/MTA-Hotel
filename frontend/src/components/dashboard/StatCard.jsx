import { formatCurrency } from "../../utils/formatters.js";

export function StatCard({ stat }) {
  const value = stat.format === "currency" ? formatCurrency(stat.value) : stat.value;

  return (
    <article className={`stat-card stat-card-${stat.tone}`}>
      <div>
        <p>{stat.label}</p>
        <strong>{value}</strong>
      </div>
      <span>{stat.support}</span>
    </article>
  );
}
