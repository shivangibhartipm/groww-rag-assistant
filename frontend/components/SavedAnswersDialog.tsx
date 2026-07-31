"use client";

import { Modal } from "./Modal";
import { BookmarkIcon, ChatIcon, ExternalIcon, TrashIcon } from "./icons";
import type { SavedEntry } from "@/lib/saved";

interface SavedAnswersDialogProps {
  entries: SavedEntry[];
  onClose: () => void;
  onOpenChat: (chatId: string) => void;
  onRemove: (messageId: string) => void;
}

export function SavedAnswersDialog({
  entries,
  onClose,
  onOpenChat,
  onRemove,
}: SavedAnswersDialogProps) {
  return (
    <Modal
      title="Saved Answers"
      subtitle={
        entries.length
          ? `${entries.length} answer${entries.length > 1 ? "s" : ""} bookmarked`
          : undefined
      }
      onClose={onClose}
    >
      {!entries.length ? (
        <div className="py-8 text-center">
          <BookmarkIcon className="mx-auto size-6 text-groww" />
          <p className="mt-2.5 text-[14px] font-semibold text-ink">
            Nothing saved yet
          </p>
          <p className="mt-1 text-[13px] text-ink-muted">
            Use Save under any answer to keep it here for later.
          </p>
        </div>
      ) : (
        <ul className="space-y-3">
          {entries.map((entry) => (
            <li
              key={entry.messageId}
              className="rounded-xl border border-[#e4ebe8] p-3.5"
            >
              <p className="text-[13px] font-bold text-ink">{entry.question}</p>
              <p className="mt-1.5 whitespace-pre-wrap text-[13px] leading-relaxed text-ink-soft">
                {entry.answer}
              </p>

              {entry.sources.length > 0 && (
                <div className="mt-2.5 flex flex-wrap gap-1.5">
                  {entry.sources.map((source) => (
                    <a
                      key={source.url}
                      href={source.url}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1.5 rounded-full bg-mint-50 px-2.5 py-1 text-[11.5px] font-medium text-groww-deep transition hover:text-groww"
                    >
                      {source.title}
                      <ExternalIcon className="size-3" />
                    </a>
                  ))}
                </div>
              )}

              <div className="mt-3 flex items-center gap-2 border-t border-line-soft pt-2.5">
                <button
                  type="button"
                  onClick={() => onOpenChat(entry.chatId)}
                  className="flex items-center gap-1.5 rounded-full border border-[#e2e8e5] px-3 py-1.5 text-[12px] font-medium text-ink-muted transition hover:border-groww hover:text-groww"
                >
                  <ChatIcon className="size-3.5" />
                  Open chat
                </button>
                <button
                  type="button"
                  onClick={() => onRemove(entry.messageId)}
                  className="flex items-center gap-1.5 rounded-full border border-[#e2e8e5] px-3 py-1.5 text-[12px] font-medium text-ink-muted transition hover:border-[#e2a99f] hover:text-[#c2543f]"
                >
                  <TrashIcon className="size-3.5" />
                  Remove
                </button>
                <span className="ml-auto truncate text-[11.5px] text-ink-muted">
                  {entry.chatTitle}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Modal>
  );
}
