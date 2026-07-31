"use client";

import { AnswerCard } from "./AnswerCard";
import { FeedbackRow, type Verdict } from "./FeedbackRow";
import { FollowUps } from "./FollowUps";
import { SchemeChoice } from "./SchemeChoice";
import { SourcesPanel } from "./SourcesPanel";
import { BotIcon, SparkleIcon } from "./icons";
import { withoutBullets } from "@/lib/answer";
import { followUpQuestions } from "@/lib/suggestions";
import type { Message } from "@/lib/types";

interface ConversationProps {
  messages: Message[];
  busy: boolean;
  feedback: Record<string, Verdict>;
  saved: Record<string, boolean>;
  onAsk: (question: string) => void;
  onVerdict: (messageId: string, verdict: Verdict) => void;
  onSave: (messageId: string) => void;
}

function BotAvatar() {
  return (
    <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-groww to-groww-dark text-white">
      <BotIcon className="size-4.5" />
    </span>
  );
}

export function Conversation({
  messages,
  busy,
  feedback,
  saved,
  onAsk,
  onVerdict,
  onSave,
}: ConversationProps) {
  if (!messages.length && !busy) {
    return (
      <div className="rounded-2xl border border-dashed border-mint-300 bg-mint-50 px-6 py-10 text-center">
        <SparkleIcon className="mx-auto size-6 text-groww" />
        <p className="mt-2.5 text-[14px] font-semibold text-ink">
          Ask a question to get started
        </p>
        <p className="mt-1 text-[13px] text-ink-muted">
          Try one of the popular questions above, or ask several questions at
          once.
        </p>
      </div>
    );
  }

  const lastAssistantId = [...messages]
    .reverse()
    .find((message) => message.role === "assistant")?.id;

  return (
    <div className="space-y-5">
      {messages.map((message, index) => {
        if (message.role === "user") {
          return (
            <div key={message.id} className="flex justify-end gap-2.5">
              <div className="max-w-[85%] rounded-2xl rounded-br-md bg-bubble px-4 py-2.5 sm:max-w-[76%]">
                <p className="whitespace-pre-wrap text-[14px] leading-relaxed text-ink">
                  {message.text}
                </p>
                <p className="mt-1 text-right text-[11px] text-[#4b7a66]">
                  {message.time}
                </p>
              </div>
              <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-mint-200 text-[11px] font-bold text-groww-deep">
                GU
              </span>
            </div>
          );
        }

        const isLatest = message.id === lastAssistantId && !busy;
        const previous = messages[index - 1];
        const askedQuestion = previous?.role === "user" ? previous.text : "";

        // A clarification is a prompt, not an answer: no rating, no follow-ups
        if (message.needsScheme) {
          return (
            <div key={message.id} className="flex gap-2.5">
              <BotAvatar />
              <div className="min-w-0 flex-1 space-y-3">
                <AnswerCard
                  answer={withoutBullets(message.text)}
                  showDisclaimer={false}
                />
                <SchemeChoice
                  options={message.schemeOptions ?? []}
                  question={askedQuestion}
                  disabled={busy}
                  onAsk={onAsk}
                />
              </div>
            </div>
          );
        }

        return (
          <div key={message.id} className="flex gap-2.5">
            <BotAvatar />
            <div className="min-w-0 flex-1 space-y-3">
              <AnswerCard answer={message.text} failed={message.failed} />
              <SourcesPanel sources={message.sources} />

              {!message.failed && (
                <FeedbackRow
                  message={message}
                  verdict={feedback[message.id]}
                  saved={Boolean(saved[message.id])}
                  onVerdict={(verdict) => onVerdict(message.id, verdict)}
                  onSave={() => onSave(message.id)}
                />
              )}

              {isLatest && !message.failed && (
                <FollowUps
                  questions={followUpQuestions(
                    message,
                    messages.slice(0, index),
                  )}
                  disabled={busy}
                  onAsk={onAsk}
                />
              )}
            </div>
          </div>
        );
      })}

      {busy && (
        <div className="flex gap-2.5">
          <BotAvatar />
          <div className="flex items-center gap-2 rounded-2xl border border-[#e4ebe8] bg-white px-4 py-3">
            <span className="flex gap-1">
              {[0, 1, 2].map((dot) => (
                <span
                  key={dot}
                  className="size-1.5 animate-bounce rounded-full bg-groww"
                  style={{ animationDelay: `${dot * 0.15}s` }}
                />
              ))}
            </span>
            <span className="text-[13px] text-ink-muted">
              Searching official documents...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
