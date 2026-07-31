import type { Chat, SourceItem } from "./types";

export interface SavedEntry {
  messageId: string;
  chatId: string;
  chatTitle: string;
  question: string;
  answer: string;
  sources: SourceItem[];
}

/** Flattens bookmarked answers across every chat, newest chat first. */
export function collectSaved(
  chats: Chat[],
  saved: Record<string, boolean>,
): SavedEntry[] {
  const entries: SavedEntry[] = [];

  for (const chat of chats) {
    chat.messages.forEach((message, index) => {
      if (message.role !== "assistant" || !saved[message.id]) return;

      const previous = chat.messages[index - 1];
      entries.push({
        messageId: message.id,
        chatId: chat.id,
        chatTitle: chat.title,
        question:
          previous?.role === "user" ? previous.text : chat.title,
        answer: message.text,
        sources: message.sources,
      });
    });
  }

  return entries;
}
