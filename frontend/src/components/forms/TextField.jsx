export function TextField({
  error,
  id,
  label,
  leftSlot,
  rightSlot,
  type = "text",
  ...props
}) {
  const errorId = error ? `${id}-error` : undefined;
  const shellClassName = [
    "input-shell",
    leftSlot ? "input-shell-with-left-slot" : "",
    rightSlot ? "input-shell-with-right-slot" : "",
    error ? "input-shell-error" : "",
  ].filter(Boolean).join(" ");

  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <div className={shellClassName}>
        {leftSlot}
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
