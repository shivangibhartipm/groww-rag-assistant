/**
 * The backend returns one formatted string per reply. For a multi-question
 * submission it looks like:
 *
 *   1. What is the expense ratio of HDFC Mid Cap Fund?
 *   The expense ratio of HDFC Mid Cap Fund is 0.75%.
 *
 *   2. What is its exit load?
 *   ...
 *
 * Citations arrive separately in `sources`, so the prose carries no URLs.
 * Parsing it into blocks lets the UI render headings and answers as real
 * elements instead of injected markup.
 */

export type AnswerBlock =
  | { kind: "heading"; text: string }
  | { kind: "text"; text: string };

const HEADING = /^\d+\.\s+/;

export function parseAnswer(answer: string): AnswerBlock[] {
  const blocks: AnswerBlock[] = [];

  for (const rawLine of answer.split("\n")) {
    const line = rawLine.trim();
    if (!line) continue;
    blocks.push(
      HEADING.test(line) ? { kind: "heading", text: line } : { kind: "text", text: line },
    );
  }

  return blocks;
}

/**
 * Removes the bulleted scheme list from a clarification reply. The UI offers
 * those options as buttons instead, so repeating them as text is noise.
 */
export function withoutBullets(text: string): string {
  return text
    .split("\n")
    .filter((line) => !line.trim().startsWith("- "))
    .join("\n")
    .trim();
}

export type TextSegment = { text: string; href?: string };

/** Splits a line so bare URLs (AMFI, SEBI) can be rendered as links. */
export function segmentLinks(text: string): TextSegment[] {
  const segments: TextSegment[] = [];
  const pattern = /https?:\/\/[^\s]+/g;
  let cursor = 0;

  for (const match of text.matchAll(pattern)) {
    const start = match.index ?? 0;
    if (start > cursor) segments.push({ text: text.slice(cursor, start) });
    // Trailing punctuation belongs to the sentence, not the URL
    const url = match[0].replace(/[.,;:)]+$/, "");
    segments.push({ text: url, href: url });
    cursor = start + url.length;
  }

  if (cursor < text.length) segments.push({ text: text.slice(cursor) });
  return segments;
}
