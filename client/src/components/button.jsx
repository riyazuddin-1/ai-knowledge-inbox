export function PrimaryButton({
  type = "button",
  disabled = false,
  onClick,
  className,
  ariaLabel,
  children,
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      aria-label={ariaLabel}
      className={`cursor-pointer bg-contrast text-foreground p-2 px-4 rounded-full disabled:opacity-50 ${className}`}
    >
      {children}
    </button>
  );
}

export default function Button({
  type = "button",
  disabled = false,
  onClick,
  className,
  ariaLabel,
  children,
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      aria-label={ariaLabel}
      className={`cursor-pointer text-text p-1 disabled:opacity-50 ${className}`}
    >
      {children}
    </button>
  );
}
