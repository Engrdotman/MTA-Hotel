import { createElement } from "react";
import { Building2, CalendarCheck, ConciergeBell } from "lucide-react";

import { BrandLogo } from "../components/common/BrandLogo.jsx";
import hotelEntrance from "../assets/hotel-entrance.jpeg";
import { brand } from "../constants/brand.js";
import { LoginForm } from "../features/auth/components/LoginForm.jsx";

const staffAreas = [
  { icon: ConciergeBell, label: "Front desk" },
  { icon: CalendarCheck, label: "Bookings" },
  { icon: Building2, label: "Guest stays" },
];

export function Login() {
  return (
    <main className="login-page">
      <section className="login-visual" aria-label="M.T.A Hotel staff portal">
        <img className="login-visual-image" src={hotelEntrance} alt="" aria-hidden="true" />
        <div className="visual-content">
          <BrandLogo className="visual-logo" showText={false} />
          <div className="visual-copy">
            <p className="brand-kicker">Internal staff portal</p>
            <h1>{brand.shortName}</h1>
            <p className="visual-system-name">Hotel Management System</p>
            <p>{brand.tagline}</p>
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
          <div className="login-card-brand">
            <BrandLogo compact showText={false} />
            <strong>{brand.shortName}</strong>
            <span>Hotel Management System</span>
          </div>
          <div className="login-heading">
            <h2>Welcome Back</h2>
            <p>Sign in to access the M.T.A Hotel Management System.</p>
          </div>
          <LoginForm />
          <footer>{brand.copyright}</footer>
        </div>
      </section>
    </main>
  );
}
