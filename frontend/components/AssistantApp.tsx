"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AboutDialog } from "./AboutDialog";
import { AskBar } from "./AskBar";
import { AssistantHeader } from "./AssistantHeader";
import { ConfirmDialog } from "./ConfirmDialog";
import { Conversation } from "./Conversation";
import type { Verdict } from "./FeedbackRow";
import { GrowwLogo } from "./GrowwLogo";
import { QuickChips } from "./QuickChips";
import { SavedAnswersDialog } from "./SavedAnswersDialog";
import { Sidebar } from "./Sidebar";
import { MenuIcon, ShieldIcon } from "./icons";
import { askAssistant, fetchStats } from "@/lib/api";
import { collectSaved } from "@/lib/saved";
import type { Chat, IndexStats, Message } from "@/lib/types";

type Dialog = "saved" | "about" | null;

const STORAGE_KEY = "groww-ai-chats-v1";
const FIRST_CHAT: Chat = { id: "chat-1", title: "New chat", messages: [] };

interface StoredState {
  chats: Chat[];
  activeChatId: string;
  feedback: Record<string, Verdict>;
  saved: Record<string, boolean>;
}

/** Restores the previous session. Runs client-side only, so the page opts out of SSR. */
function loadStore(): StoredState {
  const fallback: StoredState = {
    chats: [FIRST_CHAT],
    activeChatId: FIRST_CHAT.id,
    feedback: {},
    saved: {},
  };

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return fallback;

    const stored = JSON.parse(raw) as StoredState;
    if (!stored.chats?.length) return fallback;

    return {
      chats: stored.chats,
      activeChatId: stored.chats.some((chat) => chat.id === stored.activeChatId)
        ? stored.activeChatId
        : stored.chats[0].id,
      feedback: stored.feedback ?? {},
      saved: stored.saved ?? {},
    };
  } catch {
    return fallback;
  }
}

function titleFrom(question: string): string {
  const firstLine = question.split("\n")[0].trim();
  return firstLine.length > 52 ? `${firstLine.slice(0, 52)}...` : firstLine;
}

function newId(): string {
  return typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

/** Drops entries for messages that no longer exist, keeping storage tidy. */
function withoutKeys<T>(
  record: Record<string, T>,
  keys: Set<string>,
): Record<string, T> {
  return Object.fromEntries(
    Object.entries(record).filter(([key]) => !keys.has(key)),
  );
}

export function AssistantApp() {
  const [restored] = useState(loadStore);
  const [chats, setChats] = useState<Chat[]>(restored.chats);
  const [activeChatId, setActiveChatId] = useState(restored.activeChatId);
  const [feedback, setFeedback] = useState<Record<string, Verdict>>(
    restored.feedback,
  );
  const [saved, setSaved] = useState<Record<string, boolean>>(restored.saved);
  const [busy, setBusy] = useState(false);
  const [dialog, setDialog] = useState<Dialog>(null);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState<IndexStats>({
    indexed_chunks: 0,
    schemes: 0,
  });

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchStats().then(setStats);
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ chats, activeChatId, feedback, saved }),
      );
    } catch {
      // Ignore quota or private-mode failures
    }
  }, [chats, activeChatId, feedback, saved]);

  const activeChat =
    chats.find((chat) => chat.id === activeChatId) ?? chats[0] ?? FIRST_CHAT;
  const messages = activeChat.messages;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, busy]);

  const appendMessage = useCallback((chatId: string, message: Message) => {
    setChats((current) =>
      current.map((chat) =>
        chat.id === chatId
          ? {
              ...chat,
              title:
                chat.messages.length === 0 && message.role === "user"
                  ? titleFrom(message.text)
                  : chat.title,
              messages: [...chat.messages, message],
            }
          : chat,
      ),
    );
  }, []);

  const ask = useCallback(
    async (rawQuestion: string) => {
      const question = rawQuestion.trim();
      if (!question || busy) return;

      // Answers land in the chat that asked, even if the user navigates away
      const chatId = activeChatId;
      appendMessage(chatId, {
        id: newId(),
        role: "user",
        text: question,
        time: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      });

      setBusy(true);
      try {
        const response = await askAssistant(question);
        appendMessage(chatId, {
          id: newId(),
          role: "assistant",
          text: response.answer,
          sources: response.sources ?? [],
          needsScheme: response.needs_scheme,
          schemeOptions: response.scheme_options ?? [],
        });
      } catch (error) {
        appendMessage(chatId, {
          id: newId(),
          role: "assistant",
          text:
            error instanceof Error
              ? error.message
              : "The assistant could not answer that right now.",
          sources: [],
          failed: true,
        });
      } finally {
        setBusy(false);
      }
    },
    [activeChatId, appendMessage, busy],
  );

  function startNewChat() {
    // Reuse the current chat when it has nothing in it yet
    if (busy || !messages.length) return;

    const chat: Chat = { id: newId(), title: "New chat", messages: [] };
    setChats((current) => [chat, ...current]);
    setActiveChatId(chat.id);
  }

  function selectChat(chatId: string) {
    if (busy || chatId === activeChatId) return;

    // A chat that was opened but never used leaves nothing worth keeping
    setChats((current) =>
      current.filter((chat) => chat.id === chatId || chat.messages.length > 0),
    );
    setActiveChatId(chatId);
  }

  function deleteChat(chatId: string) {
    const target = chats.find((chat) => chat.id === chatId);
    if (!target) return;

    const remaining = chats.filter((chat) => chat.id !== chatId);
    // The sidebar always needs somewhere to land
    const next = remaining.length
      ? remaining
      : [{ id: newId(), title: "New chat", messages: [] }];

    setChats(next);
    if (activeChatId === chatId) setActiveChatId(next[0].id);

    const removedIds = new Set(target.messages.map((message) => message.id));
    setFeedback((current) => withoutKeys(current, removedIds));
    setSaved((current) => withoutKeys(current, removedIds));
  }

  function requestDeleteChat(chatId: string) {
    if (busy) return;
    const target = chats.find((chat) => chat.id === chatId);
    // Only interrupt when there is history worth losing
    if (target?.messages.length) {
      setPendingDelete(chatId);
    } else {
      deleteChat(chatId);
    }
  }

  const savedEntries = collectSaved(chats, saved);
  // A chat only earns a place in the sidebar once something has been asked in it
  const recentChats = chats.filter((chat) => chat.messages.length > 0);

  return (
    <div className="flex h-full min-w-0">
      <Sidebar
        chats={recentChats}
        activeChatId={activeChat.id}
        savedCount={savedEntries.length}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={startNewChat}
        onSelectChat={selectChat}
        onDeleteChat={requestDeleteChat}
        onOpenSaved={() => setDialog("saved")}
        onOpenAbout={() => setDialog("about")}
      />

      <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* On phones the drawer is off-canvas, so the brand and a menu live here */}
        <div className="flex shrink-0 items-center gap-2.5 border-b border-line bg-surface px-3 py-2.5 md:hidden">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            aria-label="Open menu"
            className="flex size-9 items-center justify-center rounded-full text-ink-soft transition hover:bg-mint-50 hover:text-groww"
          >
            <MenuIcon className="size-5" />
          </button>
          <GrowwLogo className="size-7 shrink-0" />
          <span className="text-[15px] font-bold text-ink">
            Groww <span className="text-groww">AI</span>
          </span>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-4xl px-4 pb-10 sm:px-6 md:px-8">
            <div className="pt-4 pb-3 md:pt-6 md:pb-4">
              <AssistantHeader />
            </div>

            <div className="sticky top-0 z-10 space-y-3 bg-surface/95 pb-3 backdrop-blur">
              <AskBar busy={busy} onAsk={ask} />
              <QuickChips disabled={busy} onAsk={ask} />
            </div>

            <div className="pt-3">
              <Conversation
                messages={messages}
                busy={busy}
                feedback={feedback}
                saved={saved}
                onAsk={ask}
                onVerdict={(messageId, verdict) =>
                  setFeedback((current) => ({ ...current, [messageId]: verdict }))
                }
                onSave={(messageId) =>
                  setSaved((current) => ({
                    ...current,
                    [messageId]: !current[messageId],
                  }))
                }
              />
            </div>

            <p className="mt-8 flex items-start justify-center gap-1.5 px-2 text-center text-[11.5px] leading-relaxed text-ink-muted sm:items-center">
              <ShieldIcon className="mt-0.5 size-3.5 shrink-0 sm:mt-0" />
              Groww AI can make mistakes. Please verify important information from
              official documents.
            </p>

            <div ref={bottomRef} />
          </div>
        </div>
      </main>

      {dialog === "saved" && (
        <SavedAnswersDialog
          entries={savedEntries}
          onClose={() => setDialog(null)}
          onOpenChat={(chatId) => {
            setActiveChatId(chatId);
            setDialog(null);
          }}
          onRemove={(messageId) =>
            setSaved((current) => ({ ...current, [messageId]: false }))
          }
        />
      )}

      {dialog === "about" && (
        <AboutDialog stats={stats} onClose={() => setDialog(null)} />
      )}

      {pendingDelete && (
        <ConfirmDialog
          title="Delete this chat?"
          message={`"${chats.find((chat) => chat.id === pendingDelete)?.title}" and its answers will be removed from this browser. This cannot be undone.`}
          confirmLabel="Delete chat"
          onConfirm={() => {
            deleteChat(pendingDelete);
            setPendingDelete(null);
          }}
          onCancel={() => setPendingDelete(null)}
        />
      )}
    </div>
  );
}
