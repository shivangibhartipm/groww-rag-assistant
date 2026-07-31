"use client";

import { ScrollRow } from "./ScrollRow";
import { ArrowRightIcon } from "./icons";

interface FollowUpsProps {
  questions: string[];
  disabled: boolean;
  onAsk: (question: string) => void;
}

export function FollowUps({ questions, disabled, onAsk }: FollowUpsProps) {
  if (!questions.length) return null;

  return (
    <section>
      <p className="mb-2 text-[12.5px] font-semibold text-ink-soft">
        You may also ask
      </p>
      <ScrollRow>
        {questions.map((question) => (
          <button
            key={question}
            type="button"
            disabled={disabled}
            onClick={() => onAsk(question)}
            className="group flex w-[210px] shrink-0 items-center gap-2 rounded-xl border border-line bg-surface px-3 py-2.5 text-left transition hover:border-groww hover:bg-mint-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <span className="line-clamp-2 flex-1 text-[12px] leading-snug text-ink-soft group-hover:text-groww">
              {question}
            </span>
            <ArrowRightIcon className="size-3.5 shrink-0 text-ink-muted group-hover:text-groww" />
          </button>
        ))}
      </ScrollRow>
    </section>
  );
}
