import { DocumentIcon, ExternalIcon } from "./icons";
import type { SourceItem } from "@/lib/types";

export function SourcesPanel({ sources }: { sources: SourceItem[] }) {
  if (!sources.length) return null;

  return (
    <section className="rounded-2xl border border-line bg-surface p-3.5">
      <div className="mb-2.5 flex items-center justify-between">
        <p className="text-[12.5px] font-bold text-ink">
          Sources ({sources.length})
        </p>
        <span className="text-[11.5px] text-ink-muted">Official pages</span>
      </div>

      <ul className="space-y-2">
        {sources.map((source) => (
          <li
            key={source.url}
            className="flex items-center gap-2.5 rounded-xl bg-mint-50 px-3 py-2.5"
          >
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-surface text-groww">
              <DocumentIcon className="size-4" />
            </span>

            <span className="min-w-0 flex-1">
              <span className="block truncate text-[13px] font-semibold text-ink">
                {source.title}
              </span>
              <span className="block truncate text-[11.5px] text-ink-muted">
                {source.subtitle}
              </span>
            </span>

            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="flex shrink-0 items-center gap-1.5 rounded-lg border border-line bg-surface px-2.5 py-1.5 text-[11.5px] font-semibold text-ink-soft transition hover:border-groww hover:text-groww"
            >
              View
              <ExternalIcon className="size-3" />
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
