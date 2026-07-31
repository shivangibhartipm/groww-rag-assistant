import { BotIcon, LockIcon, ShieldIcon, SparkleIcon } from "./icons";

const PILLS = [
  { label: "Facts Only", icon: ShieldIcon },
  { label: "No Investment Advice", icon: LockIcon },
  { label: "SEBI Compliant", icon: ShieldIcon },
];

export function AssistantHeader() {
  return (
    <header className="flex items-start gap-3.5">
      <span className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-mint-100 text-groww">
        <BotIcon className="size-7" />
      </span>

      <div className="min-w-0">
        <h1 className="flex items-center gap-2 text-[24px] font-bold tracking-tight text-ink">
          Mutual Fund Assistant
          <SparkleIcon className="size-5 text-groww" />
        </h1>
        <p className="mt-0.5 text-[13.5px] text-ink-muted">
          Ask factual questions about mutual funds and get instant answers.
        </p>

        <div className="mt-2.5 flex flex-wrap gap-2">
          {PILLS.map(({ label, icon: PillIcon }) => (
            <span
              key={label}
              className="flex items-center gap-1.5 rounded-full bg-mint-100 px-3 py-1 text-[11.5px] font-semibold text-groww-deep"
            >
              <PillIcon className="size-3.5" />
              {label}
            </span>
          ))}
        </div>
      </div>
    </header>
  );
}
