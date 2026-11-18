import Button, { PrimaryButton } from "./Button";
import InfiniteScroll from "./InfiniteScroll";

export default function Sidebar({
  items,
  isLoadingInitial,
  isLoadingMore,
  hasMore,
  error,
  onRefresh,
  onOpenAddModal,
  onLoadMore,
}) {
  const isEmpty = !isLoadingInitial && items.length === 0;

  const getStatusBadgeStyle = (status) => {
    const s = String(status).toLowerCase();
    if (s === "completed" || s === "ready" || s === "indexed") {
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    }
    if (s === "failed" || s === "error") {
      return "bg-red-500/15 text-red-400 border-red-500/30";
    }
    return "bg-amber-500/15 text-amber-400 border-amber-500/30";
  };

  if (isLoadingInitial) {
    return (
      <aside className="w-80 bg-foreground border-r border-highlight/30 flex flex-col shrink-0">
        <div className="p-4 border-b border-highlight/30 flex items-center justify-between gap-2">
          <div className="h-4 w-24 bg-background/50 rounded animate-pulse" />
          <div className="h-6 w-12 bg-background/50 rounded animate-pulse" />
        </div>
        <div className="flex-1 p-4 space-y-2 animate-pulse">
          {[1, 2, 3, 4, 5].map((n) => (
            <div key={n} className="p-3 rounded-lg bg-background/40 h-14" />
          ))}
        </div>
      </aside>
    );
  }

  if (isEmpty) {
    return (
      <aside className="w-80 bg-foreground border-r border-highlight/30 flex flex-col shrink-0">
        <div className="flex-1 p-6 flex flex-col items-center justify-center text-center">
          <div className="w-10 h-10 rounded-full bg-contrast/10 flex items-center justify-center mb-3 text-contrast font-bold text-lg">
            +
          </div>
          <h3 className="text-sm font-semibold mb-1">No Sources Yet</h3>
          <p className="text-xs opacity-60 mb-4 leading-relaxed">
            Ingest your first URL, document, or text snippet to start querying your knowledge base.
          </p>
          <PrimaryButton
            onClick={onOpenAddModal}
            className="font-medium text-xs py-2 px-4 shadow-sm"
          >
            Add First Source
          </PrimaryButton>
        </div>
      </aside>
    );
  }

  return (
    <aside className="w-80 bg-foreground border-r border-highlight/30 flex flex-col shrink-0">
      <div className="p-4 border-b border-highlight/30 flex items-center justify-between gap-2">
        <h2 className="text-sm font-semibold uppercase tracking-wider opacity-80">
          Sources ({items.length})
        </h2>
        <div className="flex items-center gap-2">
          <Button
            onClick={onRefresh}
            disabled={isLoadingInitial}
            ariaLabel="Refresh list"
            className="text-xs opacity-60 hover:opacity-100"
          >
            ↻
          </Button>
          <PrimaryButton
            onClick={onOpenAddModal}
            className="font-medium text-xs py-1 px-2.5"
          >
            + Add
          </PrimaryButton>
        </div>
      </div>

      <InfiniteScroll
        onEnd={() => {
          if (hasMore && !isLoadingMore) onLoadMore();
        }}
        className="flex-1 p-4 space-y-2"
      >
        {error && <p className="text-xs text-red-400 mb-2">{error}</p>}

        {items.map((item) => (
          <div
            key={item.id}
            className="p-2.5 rounded-lg bg-background/60 border border-highlight/40 flex flex-col gap-1 hover:border-highlight/70 transition-colors"
          >
            <div className="flex items-start justify-between gap-2">
              <span
                className="text-sm font-medium truncate"
                title={item.title || item.source || `Item #${item.id}`}
              >
                {item.title || item.source || `Untitled #${item.id}`}
              </span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded border shrink-0 uppercase font-semibold ${getStatusBadgeStyle(
                  item.status,
                )}`}
              >
                {item.status}
              </span>
            </div>
            <div className="flex items-center justify-between text-[11px] opacity-60">
              <span className="uppercase">{item.type}</span>
              <span>{new Date(item.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        ))}

        {isLoadingMore && (
          <div className="text-center py-2 text-xs opacity-50 animate-pulse">
            Loading more sources...
          </div>
        )}
      </InfiniteScroll>
    </aside>
  );
}
