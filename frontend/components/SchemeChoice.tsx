"use client";

import { ArrowRightIcon } from "./icons";

interface SchemeChoiceProps {
  options: string[];
  question: string;
  disabled: boolean;
  onAsk: (question: string) => void;
}

/** Re-asks the original question with the chosen scheme appended. */
function withScheme(question: string, scheme: string): string {
  return `${question.replace(/[?\s]+$/, "")} for ${scheme}?`;
}

export function SchemeChoice({
  options,
  question,
  disabled,
  onAsk,
}: SchemeChoiceProps) {
  if (!options.length) return null;

  return (
    <section className="rounded-2xl border border-mint-200 bg-mint-50 p-3.5">
      <p className="mb-2.5 text-[12.5px] font-bold text-groww-deep">
        Select a scheme
      </p>
      <div className="flex flex-wrap gap-2">
        {options.map((scheme) => (
          <button
            key={scheme}
            type="button"
            disabled={disabled}
            title={withScheme(question, scheme)}
            onClick={() => onAsk(withScheme(question, scheme))}
            className="group flex items-center gap-1.5 rounded-full border border-mint-300 bg-surface px-3.5 py-1.5 text-[12.5px] font-medium text-ink-soft transition hover:border-groww hover:text-groww disabled:cursor-not-allowed disabled:opacity-50"
          >
            {scheme}
            <ArrowRightIcon className="size-3.5 text-ink-muted group-hover:text-groww" />
          </button>
        ))}
      </div>
    </section>
  );
}
