export function Button({ children, icon, isLoading = false, ...props }) {
  return (
    <button className="button button-primary" disabled={isLoading || props.disabled} {...props}>
      {isLoading ? <span className="button-spinner" aria-hidden="true" /> : null}
      {icon && !isLoading ? <span className="button-icon">{icon}</span> : null}
      <span>{isLoading ? "Signing in..." : children}</span>
    </button>
  );
}
