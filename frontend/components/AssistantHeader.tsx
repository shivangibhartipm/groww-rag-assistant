import { BotIcon, LockIcon, ShieldIcon, SparkleIcon } from "./icons";
import { ThemeToggle } from "./ThemeToggle";

const PILLS = [
  { label: "Facts Only", icon: ShieldIcon },
  { label: "No Investment Advice", icon: LockIcon },
  { label: "SEBI Compliant", icon: ShieldIcon },
];

export function AssistantHeader() {
  return (
    <header className="flex items-start gap-3 sm:gap-3.5">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-2xl bg-mint-100 text-groww sm:size-12">
        <BotIcon className="size-6 sm:size-7" />
      </span>

      <div className="min-w-0 flex-1">
        <h1 className="flex flex-wrap items-center gap-2 text-[20px] font-bold tracking-tight text-ink sm:text-[24px]">
          Mutual Fund Assistant
          <SparkleIcon className="size-4 text-groww sm:size-5" />
        </h1>
        <p className="mt-0.5 text-[13px] text-ink-muted sm:text-[13.5px]">
          Ask factual questions about mutual funds and get instant answers.
        </p>

        <div className="mt-2.5 flex flex-wrap gap-1.5 sm:gap-2">
          {PILLS.map(({ label, icon: PillIcon }) => (
            <span
              key={label}
              className="flex items-center gap-1.5 rounded-full bg-mint-100 px-2.5 py-1 text-[11px] font-semibold text-groww-deep sm:px-3 sm:text-[11.5px]"
            >
              <PillIcon className="size-3.5" />
              {label}
            </span>
          ))}
        </div>
      </div>

      <ThemeToggle />
    </header>
  );
}
