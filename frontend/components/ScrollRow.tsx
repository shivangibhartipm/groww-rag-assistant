"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronRightIcon } from "./icons";

/**
 * Horizontal strip of chips or cards. The chevron only appears once the
 * content actually overflows, and it pages the strip along.
 */
export function ScrollRow({ children }: { children: React.ReactNode }) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [overflowing, setOverflowing] = useState(false);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;

    // ResizeObserver fires immediately on observe, covering the initial measure
    const observer = new ResizeObserver(() =>
      setOverflowing(track.scrollWidth > track.clientWidth + 4),
    );
    observer.observe(track);
    return () => observer.disconnect();
  }, [children]);

  return (
    <div className="flex items-center gap-2">
      <div
        ref={trackRef}
        className="no-scrollbar flex min-w-0 flex-1 gap-2 overflow-x-auto"
      >
        {children}
      </div>

      {overflowing && (
        <button
          type="button"
          aria-label="Scroll for more"
          onClick={() =>
            trackRef.current?.scrollBy({ left: 260, behavior: "smooth" })
          }
          className="flex size-7 shrink-0 items-center justify-center rounded-full border border-line bg-surface text-ink-muted transition hover:border-groww hover:text-groww"
        >
          <ChevronRightIcon className="size-4" />
        </button>
      )}
    </div>
  );
}
