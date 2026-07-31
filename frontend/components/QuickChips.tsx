"use client";

import { ScrollRow } from "./ScrollRow";
import { POPULAR_QUESTIONS } from "@/lib/suggestions";

interface QuickChipsProps {
  disabled: boolean;
  onAsk: (question: string) => void;
}

export function QuickChips({ disabled, onAsk }: QuickChipsProps) {
  return (
    <section>
      <p className="mb-2 text-[12.5px] font-semibold text-ink-soft">
        Popular Questions
      </p>
      <ScrollRow>
        {POPULAR_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            disabled={disabled}
            onClick={() => onAsk(question)}
            className="shrink-0 rounded-full border border-line bg-surface px-4 py-1.5 text-[12.5px] font-medium whitespace-nowrap text-ink-soft transition hover:border-groww hover:bg-mint-50 hover:text-groww disabled:cursor-not-allowed disabled:opacity-50"
          >
            {question}
          </button>
        ))}
      </ScrollRow>
    </section>
  );
}
