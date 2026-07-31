"use client";

import { useEffect } from "react";
import { GrowwLogo } from "./GrowwLogo";
import {
  BookmarkIcon,
  ChatIcon,
  CloseIcon,
  InfoIcon,
  PlusIcon,
  ShieldIcon,
  TrashIcon,
} from "./icons";
import type { Chat } from "@/lib/types";

interface SidebarProps {
  chats: Chat[];
  activeChatId: string;
  savedCount: number;
  open: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onSelectChat: (id: string) => void;
  onDeleteChat: (id: string) => void;
  onOpenSaved: () => void;
  onOpenAbout: () => void;
}

export function Sidebar({
  chats,
  activeChatId,
  savedCount,
  open,
  onClose,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onOpenSaved,
  onOpenAbout,
}: SidebarProps) {
  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  return (
    <>
      {/* Below md the drawer floats over the chat, so it needs a dimmed way out */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/30 md:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}

      <aside
        // 272px would leave a phone about 100px of chat, so the sidebar only
        // joins the flex row from md up and slides over the content below it.
        className={`fixed inset-y-0 left-0 z-40 flex w-[272px] shrink-0 flex-col overflow-y-auto border-r border-line bg-mint-50 px-3 py-4 transition-transform duration-200 md:static md:h-full md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="mb-4 flex items-center gap-2.5 px-1">
          <GrowwLogo className="size-8 shrink-0" />
          <span className="text-lg font-bold text-ink">
            Groww <span className="text-groww">AI</span>
          </span>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close menu"
            className="ml-auto flex size-8 items-center justify-center rounded-full text-ink-muted transition hover:bg-mint-100 hover:text-groww md:hidden"
          >
            <CloseIcon className="size-4" />
          </button>
        </div>

        <button
          type="button"
          onClick={() => {
            onNewChat();
            onClose();
          }}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-mint-300 bg-surface py-2.5 text-sm font-semibold text-groww transition hover:bg-mint-100"
        >
        <PlusIcon className="size-4" />
        New Chat
      </button>

      {chats.length > 0 && (
        <p className="mt-5 mb-1.5 px-1 text-xs font-bold text-ink-soft">
          Recent Chats
        </p>
      )}
      <nav className="flex flex-col gap-0.5">
        {chats.map((chat) => {
          const isActive = chat.id === activeChatId;
          return (
            <div
              key={chat.id}
              className={`group flex items-center rounded-lg pr-1 transition ${
                isActive ? "bg-mint-200" : "hover:bg-mint-100"
              }`}
            >
              <button
                type="button"
                onClick={() => {
                  onSelectChat(chat.id);
                  onClose();
                }}
                className={`flex min-w-0 flex-1 items-start gap-2.5 py-2 pl-2.5 text-left text-[13px] leading-snug ${
                  isActive ? "font-semibold text-ink" : "text-ink-soft"
                }`}
              >
                <ChatIcon className="mt-px size-4 shrink-0 opacity-55" />
                <span className="line-clamp-2">{chat.title}</span>
              </button>

              <button
                type="button"
                onClick={() => onDeleteChat(chat.id)}
                aria-label={`Delete chat: ${chat.title}`}
                title="Delete chat"
                className="flex size-6 shrink-0 items-center justify-center rounded-md text-ink-muted/55 transition group-hover:text-ink-muted hover:bg-surface hover:!text-danger"
              >
                <TrashIcon className="size-3.5" />
              </button>
            </div>
          );
        })}
      </nav>

        <div className="mt-4 flex flex-col gap-0.5 border-t border-line pt-2">
          <button
            type="button"
            onClick={() => {
              onOpenSaved();
              onClose();
            }}
            className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-[13px] text-ink-soft transition hover:bg-mint-100 hover:text-groww"
          >
            <BookmarkIcon className="size-4 shrink-0 opacity-55" />
            <span className="flex-1">Saved Answers</span>
            {savedCount > 0 && (
              <span className="rounded-full bg-mint-200 px-1.5 text-[11px] font-semibold text-groww-deep">
                {savedCount}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={() => {
              onOpenAbout();
              onClose();
            }}
            className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-[13px] text-ink-soft transition hover:bg-mint-100 hover:text-groww"
          >
            <InfoIcon className="size-4 shrink-0 opacity-55" />
            <span className="flex-1">About Groww AI</span>
          </button>
        </div>

        <div className="mt-auto pt-4">
          <div className="rounded-xl bg-mint-100 p-3.5 text-groww-deep">
            <p className="flex items-center gap-1.5 text-[13px] font-bold">
              <ShieldIcon className="size-4" />
              Facts Only
            </p>
            <p className="mt-1.5 text-[11.5px] leading-relaxed text-moss">
              This assistant provides factual information from official documents.
            </p>
            <p className="mt-2 text-[11.5px] font-bold">Not investment advice.</p>
          </div>

          <div className="mt-2.5 flex items-center gap-2.5 rounded-full border border-line bg-surface py-2 pr-3 pl-2">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-groww text-[11px] font-bold text-white">
              GU
            </span>
            <span className="flex-1 text-[13px] font-semibold text-ink">
              Guest User
            </span>
          </div>
        </div>
      </aside>
    </>
  );
}
