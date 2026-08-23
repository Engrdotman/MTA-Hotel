import { useState } from "react";

import logoPath from "../../assets/mTalogo.jpeg";
import { brand } from "../../constants/brand.js";

export function BrandLogo({ compact = false, showText = true, className = "" }) {
  const [logoAvailable, setLogoAvailable] = useState(true);

  return (
    <div className={`brand-logo ${compact ? "brand-logo-compact" : ""} ${className}`}>
      {logoAvailable ? (
        <img
          src={logoPath}
          alt={`${brand.shortName} logo`}
          onError={() => setLogoAvailable(false)}
        />
      ) : (
        <span className="brand-logo-mark" aria-hidden="true">
          MTA
        </span>
      )}
      {showText ? (
        <span className="brand-logo-text">
          <strong>{brand.shortName}</strong>
          <small>{brand.tagline}</small>
        </span>
      ) : null}
    </div>
  );
}
