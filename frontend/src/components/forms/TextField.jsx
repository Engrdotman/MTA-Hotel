export function TextField({
  error,
  id,
  label,
  rightSlot,
  type = "text",
  ...props
}) {
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <div className={`input-shell ${error ? "input-shell-error" : ""}`}>
        <input
          aria-describedby={errorId}
          aria-invalid={Boolean(error)}
          id={id}
          type={type}
          {...props}
        />
        {rightSlot}
      </div>
      {error ? (
        <p className="field-error" id={errorId}>
          {error}
        </p>
      ) : null}
    </div>
  );
}
