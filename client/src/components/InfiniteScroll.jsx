import { useEffect, useRef } from "react";

export default function InfiniteScroll({
  children,
  onEnd,
  threshold = 300,
  className = "",
  style,
}) {
  const containerRef = useRef(null);
  const sentinelRef = useRef(null);
  const callbackRef = useRef(onEnd);

  useEffect(() => {
    callbackRef.current = onEnd;
  }, [onEnd]);

  useEffect(() => {
    const container = containerRef.current;
    const sentinel = sentinelRef.current;

    if (!container || !sentinel) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          callbackRef.current();
        }
      },
      {
        root: container,
        rootMargin: `0px 0px ${threshold}px 0px`,
        threshold: 0,
      },
    );

    observer.observe(sentinel);

    return () => observer.disconnect();
  }, [threshold]);

  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={style}
    >
      {children}
      <div ref={sentinelRef} aria-hidden="true" style={{ width: "1px", height: "1px" }} />
    </div>
  );
}
