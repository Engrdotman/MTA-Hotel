import { createElement } from "react";
import { Building2, CalendarCheck, ConciergeBell } from "lucide-react";

import { BrandLogo } from "../components/common/BrandLogo.jsx";
import { brand } from "../constants/brand.js";
import { LoginForm } from "../features/auth/components/LoginForm.jsx";

const staffAreas = [
  { icon: ConciergeBell, label: "Front desk" },
  { icon: CalendarCheck, label: "Reservations" },
  { icon: Building2, label: "Guest stays" },
];

export function Login() {
  return (
    <main className="login-page">
      <section className="login-visual" aria-label="M.T.A Hotel staff portal">
        <div className="visual-content">
          <BrandLogo className="visual-logo" showText={false} />
          <div className="visual-copy">
            <p className="brand-kicker">{brand.hospitalityTagline}</p>
            <h1>{brand.hotelName}</h1>
            <p>{brand.tagline}</p>
          </div>
          <div className="visual-desk" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <ul className="staff-areas" aria-label="Staff workspace areas">
            {staffAreas.map(({ icon, label }) => (
              <li key={label}>
                {createElement(icon, { "aria-hidden": "true", size: 17 })}
                <span>{label}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="login-panel" aria-label="Staff sign in">
        <div className="login-card">
          <BrandLogo compact />
          <div className="login-heading">
            <h2>Staff Sign In</h2>
            <p>Access reservations, rooms, guests, billing, and reports.</p>
          </div>
          <LoginForm />
          <footer>{brand.copyright}</footer>
        </div>
      </section>
    </main>
  );
}
