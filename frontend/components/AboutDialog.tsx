"use client";

import { Modal } from "./Modal";
import { CheckIcon, CloseIcon } from "./icons";
import type { IndexStats } from "@/lib/types";

const ANSWERS = [
  "Expense ratio of a scheme",
  "Exit load details",
  "Minimum SIP amount",
  "ELSS lock-in period",
  "Riskometer classification",
  "Benchmark index",
  "Fund manager names",
  "How to download statements and capital gains reports",
];

const REFUSES = [
  "Which fund should I invest in",
  "Future returns or performance predictions",
  "Tax planning or portfolio advice",
  "Anything not found in the indexed documents",
];

export function AboutDialog({
  stats,
  onClose,
}: {
  stats: IndexStats;
  onClose: () => void;
}) {
  return (
    <Modal
      title="About Groww AI"
      subtitle="Retrieval-augmented assistant for mutual fund facts"
      onClose={onClose}
    >
      <p className="text-[13.5px] leading-relaxed text-ink-soft">
        Every answer is retrieved from official scheme pages and returned with
        the source it came from. If the corpus does not contain the fact, the
        assistant says so rather than guessing.
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-mint-50 p-3.5">
          <p className="text-[20px] font-bold text-groww">
            {stats.indexed_chunks.toLocaleString()}
          </p>
          <p className="text-[12px] text-ink-muted">Documents indexed</p>
        </div>
        <div className="rounded-xl bg-mint-50 p-3.5">
          <p className="text-[20px] font-bold text-groww">{stats.schemes}</p>
          <p className="text-[12px] text-ink-muted">Schemes covered</p>
        </div>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <section>
          <p className="mb-2 text-[12.5px] font-bold text-ink">
            What it answers
          </p>
          <ul className="space-y-1.5">
            {ANSWERS.map((item) => (
              <li
                key={item}
                className="flex items-start gap-1.5 text-[12.5px] leading-snug text-ink-soft"
              >
                <CheckIcon className="mt-0.5 size-3.5 shrink-0 text-groww" />
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section>
          <p className="mb-2 text-[12.5px] font-bold text-ink">
            What it will not do
          </p>
          <ul className="space-y-1.5">
            {REFUSES.map((item) => (
              <li
                key={item}
                className="flex items-start gap-1.5 text-[12.5px] leading-snug text-ink-soft"
              >
                <CloseIcon className="mt-0.5 size-3.5 shrink-0 text-danger" />
                {item}
              </li>
            ))}
          </ul>
        </section>
      </div>

      <p className="mt-4 rounded-xl bg-mint-50 p-3.5 text-[12px] leading-relaxed text-groww-deep">
        This assistant provides factual information only and is not investment
        advice. Mutual fund investments are subject to market risks. Read all
        scheme related documents carefully.
      </p>
    </Modal>
  );
}
