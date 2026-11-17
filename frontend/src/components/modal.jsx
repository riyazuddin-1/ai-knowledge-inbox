export default function Modal({
  children,
  onClose,
  title,
  style = "popup",
}) {
  const hasHeader = title !== undefined;

  return (
    <div
      className={`fixed inset-0 z-50 flex bg-black/50 ${style == "right" ? " items-end justify-end" : " items-center justify-center"}`}
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        className={`bg-foreground flex flex-col gap-4 overflow-hidden border-2 border-highlight p-4 ${style == "right" ? "h-full w-fit" : "w-80"}`}
        onClick={(event) => event.stopPropagation()}
      >
        {hasHeader && (
          <div className="flex items-center justify-between">
            {title !== undefined && (
              <h2 className="text-lg font-bold">{title}</h2>
            )}
            <button
              type="button"
              aria-label="Close"
              className="cursor-pointer text-text/50 hover:text-text"
              onClick={onClose}
            >
              ✕
            </button>
          </div>
        )}
        {children}
      </div>
    </div>
  );
}
