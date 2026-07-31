"use client";

import { useEffect, useRef, useState } from "react";
import { MicIcon, SendIcon } from "./icons";
import { useVoiceInput } from "@/lib/useVoiceInput";

interface AskBarProps {
  busy: boolean;
  onAsk: (question: string) => void;
}

export function AskBar({ busy, onAsk }: AskBarProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const voice = useVoiceInput((transcript) =>
    setValue((current) => (current ? `${current} ${transcript}` : transcript)),
  );

  // Grow with the question so multi-question submissions stay readable
  useEffect(() => {
    const input = inputRef.current;
    if (!input) return;
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
  }, [value]);

  function submit() {
    const question = value.trim();
    if (!question || busy) return;
    onAsk(question);
    setValue("");
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
      className="flex items-end gap-1 rounded-2xl border border-line bg-surface py-2 pr-2 pl-4 shadow-[0_1px_3px_rgba(16,24,40,0.04)] focus-within:border-groww"
    >
      <textarea
        ref={inputRef}
        rows={1}
        value={value}
        disabled={busy}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
          }
        }}
        placeholder="Ask anything about mutual funds..."
        aria-label="Ask a question"
        className="max-h-40 flex-1 resize-none bg-transparent py-2 text-[14px] text-ink outline-none placeholder:text-ink-faint disabled:opacity-60"
      />

      {voice.supported && (
        <button
          type="button"
          onClick={voice.toggle}
          aria-label={voice.listening ? "Stop dictation" : "Dictate a question"}
          className={`mb-0.5 flex size-9 items-center justify-center rounded-full transition ${
            voice.listening
              ? "bg-mint-100 text-groww"
              : "text-ink-muted hover:bg-mint-50 hover:text-groww"
          }`}
        >
          <MicIcon className="size-[18px]" />
        </button>
      )}

      <button
        type="submit"
        disabled={busy || !value.trim()}
        aria-label="Ask"
        className="mb-0.5 flex size-9 items-center justify-center rounded-full bg-groww text-white transition hover:bg-groww-dark disabled:cursor-not-allowed disabled:opacity-40"
      >
        <SendIcon className="size-[17px]" />
      </button>
    </form>
  );
}
