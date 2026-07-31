"use client";

import { useEffect, useState } from "react";
import {
  BookmarkIcon,
  CheckIcon,
  CopyIcon,
  ShareIcon,
  ThumbDownIcon,
  ThumbUpIcon,
} from "./icons";
import type { AssistantMessage } from "@/lib/types";

export type Verdict = "up" | "down";

interface FeedbackRowProps {
  message: AssistantMessage;
  verdict?: Verdict;
  saved: boolean;
  onVerdict: (verdict: Verdict) => void;
  onSave: () => void;
}

const BUTTON =
  "flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[12px] font-medium whitespace-nowrap transition";
const IDLE =
  "border-line bg-surface text-ink-muted hover:border-groww hover:text-groww";
const ACTIVE = "border-groww bg-mint-100 text-groww";

export function FeedbackRow({
  message,
  verdict,
  saved,
  onVerdict,
  onSave,
}: FeedbackRowProps) {
  const [flash, setFlash] = useState<string>("");

  useEffect(() => {
    if (!flash) return;
    const timer = setTimeout(() => setFlash(""), 1800);
    return () => clearTimeout(timer);
  }, [flash]);

  async function copy(text: string, note: string) {
    try {
      await navigator.clipboard.writeText(text);
      setFlash(note);
    } catch {
      setFlash("Copy blocked by browser");
    }
  }

  async function share() {
    const links = message.sources.map((source) => source.url).join("\n");
    const payload = links ? `${message.text}\n\nSources:\n${links}` : message.text;

    if (navigator.share) {
      try {
        await navigator.share({ title: "Groww AI answer", text: payload });
        return;
      } catch {
        // Cancelled or unsupported, fall through to clipboard
      }
    }
    await copy(payload, "Answer and sources copied");
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-[12px] text-ink-muted">Was this helpful?</span>

      <button
        type="button"
        onClick={() => onVerdict("up")}
        className={`${BUTTON} ${verdict === "up" ? ACTIVE : IDLE}`}
      >
        <ThumbUpIcon className="size-3.5" />
        Helpful
      </button>

      <button
        type="button"
        onClick={() => onVerdict("down")}
        className={`${BUTTON} ${verdict === "down" ? ACTIVE : IDLE}`}
      >
        <ThumbDownIcon className="size-3.5" />
        Not Helpful
      </button>

      <span className="mx-0.5 h-4 w-px bg-line" />

      <button
        type="button"
        onClick={() => copy(message.text, "Answer copied")}
        className={`${BUTTON} ${IDLE}`}
      >
        <CopyIcon className="size-3.5" />
        Copy
      </button>

      <button type="button" onClick={share} className={`${BUTTON} ${IDLE}`}>
        <ShareIcon className="size-3.5" />
        Share
      </button>

      <button
        type="button"
        onClick={onSave}
        className={`${BUTTON} ${saved ? ACTIVE : IDLE}`}
      >
        <BookmarkIcon className="size-3.5" />
        {saved ? "Saved" : "Save"}
      </button>

      {flash && (
        <span className="flex items-center gap-1 text-[12px] font-medium text-groww">
          <CheckIcon className="size-3.5" />
          {flash}
        </span>
      )}
      {verdict && !flash && (
        <span className="text-[12px] text-ink-muted">Thanks for the feedback.</span>
      )}
    </div>
  );
}
