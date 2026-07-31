import type { AssistantMessage, Message } from "./types";

// Spelled out in full so the chip shows exactly which scheme it will ask about
export const POPULAR_QUESTIONS: string[] = [
  "Who is the fund manager of HDFC Mid Cap Fund?",
  "What is the expense ratio of HDFC Mid Cap Fund?",
];

const TEMPLATES = [
  { fact: "expense ratio", text: "What is the expense ratio of {scheme}?" },
  { fact: "exit load", text: "What is the exit load of {scheme}?" },
  {
    fact: "minimum sip",
    text: "What is the minimum SIP amount for {scheme}?",
  },
  { fact: "benchmark", text: "What is the benchmark index of {scheme}?" },
  { fact: "fund manager", text: "Who is the fund manager of {scheme}?" },
  {
    fact: "riskometer",
    text: "What is the riskometer classification of {scheme}?",
  },
];

const FACT_PATTERNS: { fact: string; pattern: RegExp }[] = [
  { fact: "expense ratio", pattern: /expense\s+ratio/i },
  { fact: "exit load", pattern: /exit\s+load/i },
  { fact: "minimum sip", pattern: /minimum\s+sip|sip\s+amount/i },
  { fact: "benchmark", pattern: /benchmark/i },
  { fact: "fund manager", pattern: /fund\s+manager|who\s+(is|manages)/i },
  { fact: "riskometer", pattern: /riskometer|risk\s+class/i },
];

const GENERIC = [
  "What is the expense ratio of HDFC Large Cap Fund?",
  "What is the exit load of HDFC Mid Cap Fund?",
  "What is the ELSS lock-in period of HDFC ELSS Tax Saver Fund?",
  "How do I download my capital gains statement?",
];

function coveredFacts(...texts: string[]): Set<string> {
  const joined = texts.join("\n");
  return new Set(
    FACT_PATTERNS.filter(({ pattern }) => pattern.test(joined)).map(
      ({ fact }) => fact,
    ),
  );
}

/**
 * Suggests further factual questions about the scheme just discussed,
 * skipping anything already asked or answered in this conversation.
 */
export function followUpQuestions(
  answer: AssistantMessage,
  history: Message[],
): string[] {
  const scheme = answer.sources.find(
    (source) => source.subtitle === "Groww scheme page",
  )?.title;
  if (!scheme) return GENERIC;

  const priorUserText = history
    .filter((message) => message.role === "user")
    .map((message) => message.text)
    .join("\n");

  // Pronouns ("its expense ratio") match the fact but not the full template
  const alreadyCovered = coveredFacts(priorUserText, answer.text);

  const suggestions = TEMPLATES.map(({ fact, text }) => ({
    fact,
    question: text.replace("{scheme}", scheme),
  }))
    .filter(
      ({ fact, question }) =>
        !alreadyCovered.has(fact) &&
        !priorUserText.toLowerCase().includes(question.toLowerCase()),
    )
    .map(({ question }) => question);

  return suggestions.length ? suggestions.slice(0, 4) : GENERIC;
}
