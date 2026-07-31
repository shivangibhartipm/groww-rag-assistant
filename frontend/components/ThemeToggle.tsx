"use client";

import { useState } from "react";

import { applyTheme, currentTheme, type Theme } from "@/lib/theme";

import { MoonIcon, SunIcon } from "./icons";

export function ThemeToggle() {
  // Seeded from the class the init script already set, so the icon matches what
  // is on screen instead of showing light and correcting itself after mount.
  const [theme, setTheme] = useState<Theme>(currentTheme);

  const next: Theme = theme === "dark" ? "light" : "dark";

  return (
    <button
      type="button"
      onClick={() => {
        applyTheme(next);
        setTheme(next);
      }}
      title={`Switch to ${next} theme`}
      aria-label={`Switch to ${next} theme`}
      className="flex size-9 shrink-0 items-center justify-center rounded-full border border-line bg-surface text-ink-soft transition hover:border-groww hover:text-groww"
    >
      {theme === "dark" ? (
        <SunIcon className="size-4.5" />
      ) : (
        <MoonIcon className="size-4.5" />
      )}
    </button>
  );
}
