import { CreditCard, LogIn, Plus, UserPlus } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function QuickActions() {
  const navigate = useNavigate();

  const actions = [
    { label: "New Booking", icon: Plus, path: "/reservations" },
    { label: "Add Guest", icon: UserPlus, path: "/guests" },
    { label: "Check-in Guest", icon: LogIn, path: "/check-in" },
    { label: "Record Payment", icon: CreditCard, path: "/billing" },
  ];

  const handleAction = (path) => {
    navigate(path);
  };

  return (
    <section className="dashboard-card quick-actions-card">
      <div className="card-heading">
        <h2>Quick Actions</h2>
        <p>Navigate to key tasks</p>
      </div>

      <div className="quick-actions-grid">
        {actions.map((action) => (
          <button 
            key={action.label} 
            onClick={() => handleAction(action.path)} 
            type="button"
            title={action.label}
          >
            <action.icon aria-hidden="true" size={18} />
            <span>{action.label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
