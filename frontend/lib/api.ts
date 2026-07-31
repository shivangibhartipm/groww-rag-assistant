import type { IndexStats, QueryResponse } from "./types";

export class AssistantError extends Error {}

export async function askAssistant(query: string): Promise<QueryResponse> {
  const response = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new AssistantError(
      payload?.detail ?? "The assistant could not answer that right now.",
    );
  }
  return payload as QueryResponse;
}

export async function fetchStats(): Promise<IndexStats> {
  try {
    const response = await fetch("/api/stats");
    if (!response.ok) throw new Error();
    return (await response.json()) as IndexStats;
  } catch {
    return { indexed_chunks: 0, schemes: 0 };
  }
}
