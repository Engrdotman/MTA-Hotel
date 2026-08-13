import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

import "../styles/users.css";

export function Unauthorized() {
  return (
    <main className="dashboard-page unauthorized-page">
      <section className="dashboard-card unauthorized-card">
        <h2>Access Denied</h2>
        <p>You do not have permission to access this page.</p>
        <Link className="rooms-primary-button" to="/dashboard">
          <ArrowLeft aria-hidden="true" size={18} />
          Back to Dashboard
        </Link>
      </section>
    </main>
  );
}
