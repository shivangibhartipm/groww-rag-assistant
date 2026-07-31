import { parseAnswer, segmentLinks } from "@/lib/answer";
import { InfoIcon } from "./icons";

function LinkedText({ text }: { text: string }) {
  return (
    <>
      {segmentLinks(text).map((segment, index) =>
        segment.href ? (
          <a
            key={index}
            href={segment.href}
            target="_blank"
            rel="noreferrer"
            className="font-medium text-groww underline decoration-mint-300 underline-offset-2 hover:decoration-groww"
          >
            {segment.text}
          </a>
        ) : (
          <span key={index}>{segment.text}</span>
        ),
      )}
    </>
  );
}

export function AnswerCard({
  answer,
  failed,
  showDisclaimer = true,
}: {
  answer: string;
  failed?: boolean;
  showDisclaimer?: boolean;
}) {
  const blocks = parseAnswer(answer);

  return (
    <div
      className={`rounded-2xl border bg-surface p-4 shadow-[0_1px_3px_rgba(16,24,40,0.04)] ${
        failed ? "border-danger-soft" : "border-line"
      }`}
    >
      <div className="space-y-2">
        {blocks.map((block, index) => {
          if (block.kind === "heading") {
            return (
              <p
                key={index}
                className={`text-[14px] font-bold text-ink ${index ? "pt-2" : ""}`}
              >
                {block.text}
              </p>
            );
          }

          return (
            <p key={index} className="text-[14px] leading-relaxed text-ink-soft">
              <LinkedText text={block.text} />
            </p>
          );
        })}
      </div>

      {showDisclaimer && (
        <p className="mt-3.5 flex items-start gap-1.5 border-t border-line-soft pt-2.5 text-[11.5px] text-ink-muted">
          <InfoIcon className="mt-px size-3.5 shrink-0" />
          Factual information only. This is not investment advice.
        </p>
      )}
    </div>
  );
}
