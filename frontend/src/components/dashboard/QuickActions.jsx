import { CreditCard, LogIn, Plus, UserPlus } from "lucide-react";

const actions = [
  { label: "New Reservation", icon: Plus },
  { label: "Add Guest", icon: UserPlus },
  { label: "Check-in Guest", icon: LogIn },
  { label: "Record Payment", icon: CreditCard },
];

export function QuickActions({ onAction }) {
  return (
    <section className="dashboard-card quick-actions-card">
      <div className="card-heading">
        <h2>Quick Actions</h2>
        <p>Shortcuts are placeholders until modules are built.</p>
      </div>

      <div className="quick-actions-grid">
        {actions.map((action) => (
          <button key={action.label} onClick={() => onAction(action.label)} type="button">
            <action.icon aria-hidden="true" size={18} />
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
