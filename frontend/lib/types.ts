export interface SourceItem {
  url: string;
  title: string;
  subtitle: string;
}

/** Shape returned by the FastAPI /query endpoint. */
export interface QueryResponse {
  answer: string;
  source: string;
  sources: SourceItem[];
  /** True when the question named no scheme and the user must pick one */
  needs_scheme: boolean;
  scheme_options: string[];
  last_updated: string;
  chunks_retrieved: number;
  tokens_used: number;
  context_used: boolean;
  error: string | null;
}

export interface IndexStats {
  indexed_chunks: number;
  schemes: number;
}

export interface UserMessage {
  id: string;
  role: "user";
  text: string;
  time: string;
}

export interface AssistantMessage {
  id: string;
  role: "assistant";
  text: string;
  sources: SourceItem[];
  needsScheme?: boolean;
  schemeOptions?: string[];
  failed?: boolean;
}

export type Message = UserMessage | AssistantMessage;

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
}
